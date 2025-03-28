from rest_framework import permissions


class IsAuthenticatedContest(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.contestuser and request.user.contestuser.is_active)
