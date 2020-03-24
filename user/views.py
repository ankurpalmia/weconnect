import hashlib

from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, status, views
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     GenericAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from user.models import LoginToken, UserProfile
from user.serializers import (CheckPasswordToken, EmailVerifySerializer,
                              ForgotPasswordSerializer, LoginSerializer,
                              ResetPasswordSerializer, UserProfileSerializer,
                              UserSerializer)
from weconnect.tasks import forgot_password_mail_task


class UserViewset(ModelViewSet):
    """
    This viewset is for user signup
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer


class GetUserDetails(RetrieveAPIView):
    """
    This view returns the details of the logged in user 
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)
        

class LoginView(CreateAPIView):
    """
    This viewset is used for Login 
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, created = LoginToken.objects.get_or_create(user=user)

        return Response({'token': token.key})


class LogoutView(DestroyAPIView):
    """
    This viewset is used to remove token after logout
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        LoginToken.objects.get(user=user).delete()
        return Response("Logout Successful", status=status.HTTP_200_OK) 

        
class GetProfileView(RetrieveAPIView):
    """
    This view will return the requested user profile
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            username=self.request.query_params.get('username')
        )
        

class EmailVerifyView(CreateAPIView):
    """
    This view is used for verifying email token
    If the token is valid, it makes verified as True
    """
    queryset = UserProfile.objects.all()
    serializer_class = EmailVerifySerializer


class SendForgotPasswordMailView(CreateAPIView):
    """
    This view takes a username and then send email with reset password token
    """
    queryset = UserProfile.objects.all()
    serializer_class = ForgotPasswordSerializer


class ForgotPasswordView(CreateAPIView):
    """
    This view verifies the token and returns the pk value for the user
    """
    queryset = UserProfile.objects.all()
    serializer_class = CheckPasswordToken


class ResetPasswordView(UpdateAPIView):
    """
    This view takes pk and the new password for password reset
    """
    queryset = UserProfile.objects.all()
    serializer_class = ResetPasswordSerializer
