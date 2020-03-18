from django.shortcuts import render
from post.models import Post, Friend
from user.models import UserProfile
from post.serializers import PostSerializer, GetPostSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from post.permissions import IsVerifiedOwner
from post.utils import get_friends
from django.db.models import Q


class PostViewSet(ModelViewSet):
    """
    This serializer is for users' posts
    """
    permission_classes = [permissions.IsAuthenticated, IsVerifiedOwner]
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
        all_friends = get_friends(user)
        all_posts = Post.objects.filter(created_by=user)
        for friend in all_friends:
            posts = Post.objects.filter(
                Q(created_by=friend, privacy='PUBLIC') | 
                Q(created_by=friend, privacy='FRIENDS'))
            all_posts |= posts
        custom_list_posts = user.post_by_friends.all()
        all_posts |= custom_list_posts
        all_posts = all_posts.order_by('-created_at')
        
        serializer = self.serializer_class(all_posts, many=True)

        return Response(serializer.data)


class UserProfileView(ListAPIView):
    """
    This view will return all the posts for a user profile
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GetPostSerializer

    def list(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        username = get_object_or_404(UserProfile, username=username)
        requested_by = request.user
        all_friends = get_friends(username)
        
        def is_friend():
            if requested_by in all_friends:
                return Q(created_by=username, privacy='FRIENDS')
            else :
                return Q()

        all_posts = Post.objects.filter(
            is_friend() |
            Q(created_by=username, privacy='PUBLIC') | 
            Q(created_by=username, privacy='CUSTOM', custom_list=requested_by.pk))
        
        all_posts = all_posts.order_by('-created_at')
        
        serializer = self.serializer_class(all_posts, many=True)
        return Response(serializer.data)

