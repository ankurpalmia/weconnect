from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, DestroyAPIView, RetrieveAPIView
from user.models import UserProfile, LoginToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, views, status
from user.serializers import UserSerializer, LoginSerializer, UserProfileSerializer
from django.shortcuts import get_object_or_404



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
