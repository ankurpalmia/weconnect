from django.shortcuts import render
from rest_framework import viewsets
from user.models import UserProfile
from user.serializers import UserSerializer


class UserViewset(viewsets.ModelViewSet):
    """
    This viewset is for user signup
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer