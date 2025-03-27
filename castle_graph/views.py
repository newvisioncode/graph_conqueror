from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Invite, ContestUser
from .serializers import InviteSerializer


# Create your views here.


class CreateInviteView(CreateAPIView):
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer

    def create(self, request, *args, **kwargs):
        serializer: InviteSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO: send email
        invite = serializer.save()
        headers = self.get_success_headers(serializer.data)

        return Response({
            'invite': serializer.data,
        }, status=status.HTTP_201_CREATED, headers=headers)


class AcceptInviteView(APIView):
    def post(self, request):
        uuid = request.data.get('uuid')
        accepted: bool = request.data.get('accepted')

        invite = Invite.objects.get(uuid=uuid)

        if invite is None:
            return Response({
                'error': 'Invite not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if invite.user.group is not None:
            return Response({
                'error': 'User is already in a group'
            }, status=status.HTTP_400_BAD_REQUEST)

        if invite.user.user != request.user:
            return Response({
                'error': 'Invite user is not the owner of the invite'
            }, status=status.HTTP_403_FORBIDDEN)

        c_user: ContestUser = ContestUser.objects.filter(user=request.user).first()

        if c_user is None:
            return Response({
                'error': 'User has not registered for the contest'
            })

        if accepted:
            invite.status = Invite.InviteStatus.ACCEPTED
        else:
            invite.status = Invite.InviteStatus.REJECTED
        invite.save()

        c_user.group = invite.group
        c_user.save()

        return Response({
            'invite': invite.uuid,
        }, status=status.HTTP_202_ACCEPTED)
