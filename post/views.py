from django.shortcuts import render
from post.models import Post, Friend
from user.models import UserProfile
from post.serializers import PostSerializer, GetPostSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import permissions


class PostViewSet(ModelViewSet):
    """
    This serializer is for users' posts
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class GetPostsView(ListAPIView):
    """
    This view will get all posts for a user's feed
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GetPostSerializer

    def list(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

