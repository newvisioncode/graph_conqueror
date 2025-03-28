from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import EmailMessage
from rest_framework.viewsets import ViewSet
from .models import Invite, ContestUser
from .permissions import IsAuthenticatedContest
from .serializers import InviteSerializer
from django.contrib.sites.shortcuts import get_current_site


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
