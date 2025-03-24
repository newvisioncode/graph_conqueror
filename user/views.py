from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, permissions, status, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .serializers import SignupSerializer, LoginSerializer

User = get_user_model()


# Create your views here.

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        print(f"ball: {user.id}")
        headers = self.get_success_headers(serializer.data)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'auth': serializer.data,
            'token': token.key,
            'created': created
        }, status=status.HTTP_201_CREATED, headers=headers)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.data)
        if user is None:
            raise exceptions.AuthenticationFailed()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'auth': serializer.data,
            'token': token.key,
            'created': created
        })