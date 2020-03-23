import hashlib

from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, status, views
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     RetrieveAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from user.models import LoginToken, UserProfile
from user.serializers import (LoginSerializer, UserProfileSerializer,
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

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        requested_user = request.query_params.get('username')

        get_user = get_object_or_404(UserProfile, username=requested_user)
        serializer = self.serializer_class(get_user, context={'request': request})
        return Response(serializer.data)
        

class EmailVerifyView(APIView):

    def post(self, request, *args, **kwargs):
        token = request.data['token']
        user_obj = get_object_or_404(UserProfile, email_token=token)
        if user_obj.verified:
            return Response("Already verified", status=status.HTTP_400_BAD_REQUEST)
        user_obj.verified = True
        user_obj.save()
        return Response("Verified successfully", status=status.HTTP_200_OK)


class SendForgotPasswordMailView(APIView):

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        user_obj = get_object_or_404(UserProfile, username=username)
        email = user_obj.email
        token = hashlib.md5(username.encode()).hexdigest()
        forgot_password_mail_task.delay(email, token)
        user_obj.forgot_pass_token = token
        user_obj.save()
        return Response("Email sent", status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):

    def post(self, request, *args, **kwargs):
        token = request.data['token']
        user_obj = get_object_or_404(UserProfile, forgot_pass_token=token)
        user_obj.forgot_pass_token = ""
        user_obj.save()
        return Response(user_obj.pk, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):

    def post(self, request, *args, **kwargs):
        password = request.data['password']
        pk = request.data['pk']

        user_obj = UserProfile.objects.get(pk=pk)
        user_obj.password = make_password(password)
        user_obj.save()
        return Response(status=status.HTTP_200_OK)
