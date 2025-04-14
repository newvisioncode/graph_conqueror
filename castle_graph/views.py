import threading

import requests
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES
from rest_framework_simplejwt.tokens import RefreshToken

from graph_conqueror.pagination import PageNumberPagination
from .models import Invite, ContestUser, SubmissionItem, CaptureCastle, Castle, Gif, Submission
from .permissions import IsAuthenticatedContest, ConfirmJudge0SubmissionPermission
from .serializers import InviteSerializer, RegisterContestUserSerializer, ContestGroupSerializer, SubmissionSerializer, \
    GifSerializer, CastleSerializer, SubmissionListSerializer, SubmissionItemSerializer


class InviteView(ViewSet):
    http_method_names = ['post']
    queryset = Invite.objects.all()
    permission_classes = (IsAuthenticatedContest,)

    def create(self, request, *args, **kwargs):
        serializer: InviteSerializer = InviteSerializer(data=request.data, context={
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        })
        serializer.is_valid(raise_exception=True)
        invite = serializer.save()
        current_site = get_current_site(request)
        message = f"{current_site.domain}/graph_conqueror/invite/{invite.uuid}"
        mail_subject = 'You invited.'
        email = EmailMessage(mail_subject, message, to=[invite.invited_user.user.email])
        email.send()
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path=r"(?P<uuid>[^/.]+)", permission_classes=[AllowAny])
    def change_state(self, request, uuid):
        accepted: bool = request.data.get('accepted', True)

        invite = Invite.objects.select_related('invited_user').get(uuid=uuid)

        if invite is None:
            return Response({
                'error': 'Invite not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if invite.invited_user.group is not None:
            return Response({
                'error': 'User is already in a group'
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user_count = ContestUser.objects.filter(group_id=invite.group_id).count()
            if user_count >= 3:
                return Response({
                    'error': 'group is full'
                }, status=status.HTTP_400_BAD_REQUEST)
            if accepted:
                invite.status = Invite.InviteStatus.ACCEPTED
            else:
                invite.status = Invite.InviteStatus.REJECTED
            invite.save()
            invite.invited_user.group = invite.group
            invite.invited_user.save()

        mail_subject = 'Your invite'

        if accepted:
            message = f"Your invite has been accepted by {invite.invited_user.user.email}"
        else:
            message = f"your invite has been rejected by {invite.invited_user.user.email}"

        email = EmailMessage(mail_subject, message, to=[invite.group.lead_user.user.email])
        email.send()
        return Response(status=status.HTTP_202_ACCEPTED)


class AuthViewSet(ViewSet):
    http_method_names = ['post']

    def get_authenticate_header(self, request):
        if self.action == 'refresh':
            return '{} realm="{}"'.format(
                AUTH_HEADER_TYPES[0],
                'api',
            )
        return super().get_authenticate_header(request)

    @action(methods=['POST'], detail=False, permission_classes=[AllowAny])
    def register(self, request):
        user_serializer = RegisterContestUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user, contest_user = user_serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'payment_id': contest_user.payment_identifier
        }, status=status.HTTP_201_CREATED)


class GroupViewSet(ViewSet):
    http_method_names = ['post']
    permission_classes = (IsAuthenticatedContest,)

    def create(self, request, *args, **kwargs):
        if request.user.contestuser.group is not None:
            raise ValidationError("you already in group. you cannot create a group.")

        serializer = ContestGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


JUDGE0_HOST = settings.JUDGE0_HOST
JUDGE0_KEY = settings.JUDGE0_KEY


class SubmissionView(ViewSet):
    http_method_names = ['post', 'put']

    def get_permissions(self):
        if self.request.method == "PUT":
            return [ConfirmJudge0SubmissionPermission()]
        return [IsAuthenticatedContest()]

    @classmethod
    def __captured_check(cls, castle, group_id):
        for neighbor in castle.neighbors:
            target_castle = Castle.objects.get(identifier=neighbor)
            captured_neighbors_count = CaptureCastle.objects.filter(
                castle__in=target_castle.neighbors,
                group_id=group_id
            ).count()

            if captured_neighbors_count == len(target_castle.neighbors):
                captured_castle = CaptureCastle.objects.filter(castle=target_castle, is_valid=True).first()
                if captured_castle:
                    captured_castle.is_valid = False
                    captured_castle.save()
                CaptureCastle.objects.create(castle=target_castle, group_id=group_id, submission=None,
                                             cause=CaptureCastle.CaptureCause.CONQUERED)

    @classmethod
    def __solved_check(cls, submission):
        is_solved = not SubmissionItem.objects.filter(
            submission=submission
        ).exclude(result=SubmissionItem.SubmissionResult.ACCEPTED).exists()
        if is_solved:
            castle = submission.castle
            CaptureCastle.objects.create(castle=castle, submission=submission,
                                         group_id=submission.group_id)
            cls.__captured_check(castle, submission.group_id)

    @staticmethod
    def __judge0_submit(request, code, language_id, question_item, submission_id):
        url = request.build_absolute_uri(reverse('castle_graph:submission-result'))
        print(url)
        response = requests.post(f"{JUDGE0_HOST}/submissions/",
                                 data={"source_code": code, 'language_id': language_id,
                                       "stdin": question_item.input, 'expected_output': question_item.output,
                                       'callback_url': f"{url}?token={JUDGE0_KEY}"})

        res = response.json()

        if response.status_code != 201 or not res.get('token', None) or res['token'] == '':
            SubmissionItem.objects.create(submission_id=submission_id, question_item=question_item,
                                          token=res.get('token', None),
                                          result=res.get('status', dict()).get('id',
                                                                               SubmissionItem.SubmissionResult.UNKNOWN_ERROR))

        SubmissionItem.objects.create(submission_id=submission_id, question_item=question_item,
                                      token=res['token'])

    def create(self, request, *args, **kwargs):
        user = request.user.contestuser
        group = user.group
        submission_serializer = SubmissionSerializer(data=request.data,
                                                     context={'request': request, 'group': group, 'contest_user': user})
        submission_serializer.is_valid(raise_exception=True)
        submission = submission_serializer.save()
        question = submission.castle.question
        code = submission.source_code.read()
        for question_item in question.questionitem_set.all():
            thread = threading.Thread(target=self.__judge0_submit,
                                      args=(
                                          request, code, submission.language.judge0_code, question_item, submission.id))
            thread.start()

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['put'], detail=False, url_path='result', url_name='result')
    def submit_result(self, request, *args, **kwargs):
        submission_item = SubmissionItem.objects.filter(token=request.data['token']).first()
        if not submission_item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        submission_item.result = request.data['status']['id']
        submission_item.runtime = request.data['time']
        submission_item.save()
        if request.data['status']['id'] == SubmissionItem.SubmissionResult.ACCEPTED:
            self.__solved_check(submission_item.submission)
        return Response(status=status.HTTP_200_OK)


class GifViewSet(GenericViewSet):
    http_method_names = ['post', 'get', 'patch']
    permission_classes = (IsAuthenticatedContest,)
    serializer_class = GifSerializer
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = Gif.objects.filter(Q(confirmed=True) | Q(user=request.user)).order_by("-id")

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        serializer = self.get_serializer(paginated_queryset, many=True)
        return Response(paginator.get_paginated_response(serializer.data).data)

    @action(methods=['get'], detail=False, url_path="requests", permission_classes=[IsAdminUser])
    def gif_requests(self, request, *args, **kwargs):
        queryset = Gif.objects.all().order_by("-id")

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        serializer = self.get_serializer(paginated_queryset, many=True)
        return Response(paginator.get_paginated_response(serializer.data).data)

    @action(methods=['patch'], detail=True, url_path="confirm", permission_classes=[IsAdminUser])
    def confirm_gif_request(self, request, *args, **kwargs):
        instance = get_object_or_404(Gif, id=kwargs["pk"])
        instance.confirmed = True
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CastleView(GenericViewSet):
    http_method_names = ['get']
    serializer_class = CastleSerializer
    permission_classes = (IsAuthenticatedContest,)
    queryset = Castle.objects.all().order_by("-id")

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class SubmissionListView(GenericViewSet):
    http_method_names = ['get']
    permission_classes = (IsAuthenticatedContest,)
    serializer_class = SubmissionListSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        print(Submission.objects.filter().prefetch_related(
            'castle',
            'castle__question',
        ).order_by("created").first().group.name)

        return Submission.objects.filter(group__contestuser__user=self.request.user).prefetch_related(
            'castle',
            'castle__question',
        ).order_by("created")

    def list(self, request, *args, **kwargs):
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(self.get_queryset(), request, view=self)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return Response(paginator.get_paginated_response(serializer.data).data)


class SubmissionItemView(GenericViewSet):
    http_method_names = ['get']
    permission_classes = (IsAuthenticatedContest,)
    serializer_class = SubmissionItemSerializer
    queryset = SubmissionItem.objects.all()

    def list(self, request, *args, **kwargs):
        id: str = self.request.query_params.get('id', None)
        if id is None or not id.isnumeric():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        submission = Submission.objects.filter(id=int(id), group__contestuser__user=self.request.user)
        if not submission.exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(SubmissionItem.objects.filter(submission=submission.first()), many=True)
        return Response(serializer.data)
