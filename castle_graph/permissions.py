from rest_framework import permissions
from django.conf import settings

JUDGE0_KEY = settings.JUDGE0_KEY


class ConfirmJudge0SubmissionPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        token = request.query_params.get('token')
        return token == JUDGE0_KEY


class IsAuthenticatedContest(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.contestuser and request.user.contestuser.is_active)
