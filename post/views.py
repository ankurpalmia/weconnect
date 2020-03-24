from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from post.models import Friend, Post
from post.permissions import IsVerifiedOwner
from post.serializers import (GetPostSerializer, LikeUnlikeSerializer,
                              PostSerializer, RespondSerializer,
                              SendRequestSerializer, UserForPost)
from post.utils import get_friends
from user.models import UserProfile
from weconnect.tasks import send_friend_request_task


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
    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        user = request.user
        all_friends = get_friends(user)
        all_posts = Post.objects.filter(created_by=user)

        posts = Post.objects.filter(
            Q(created_by__in=all_friends) &
            (Q(privacy='PUBLIC') | Q(privacy='FRIENDS'))
        )
        all_posts |= posts
        
        custom_list_posts = user.post_by_friends.all()
        all_posts |= custom_list_posts
        all_posts = all_posts.order_by('-created_at')
        
        serializer = self.serializer_class(all_posts.distinct(), many=True, context={'request': request})
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)    


class UserProfilePostsView(ListAPIView):
    """
    This view will return all the posts for a user profile
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GetPostSerializer
    pagination_class = PageNumberPagination

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
        
        def is_same_user():
            if requested_by == username:
                return Q(created_by=username) & (Q(privacy='PRIVATE') | Q(privacy='CUSTOM') | Q(privacy='FRIENDS'))
            else:
                return Q(created_by=username, privacy='CUSTOM', custom_list=requested_by.pk)

        all_posts = Post.objects.filter(
            is_friend() | is_same_user() |
            Q(created_by=username, privacy='PUBLIC'))
        
        all_posts = all_posts.order_by('-created_at')
        
        serializer = self.serializer_class(all_posts, many=True, context={'request': request})
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class GetAllFriendsView(ListAPIView):
    """
    This view returns a list of friends of a user
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserForPost

    def get(self, request, *args, **kwargs):
        user = request.user
        all_friends = get_friends(user)
        serializer = self.serializer_class(all_friends, many=True)
        return Response(serializer.data)


class SendRequestView(CreateAPIView):
    """
    This view takes a sender and receiver to send friend request over mail
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SendRequestSerializer


class RespondRequest(CreateAPIView):
    """
    This view takes sender, receiver and the response of the receiver for friend request
    """
    queryset = Friend.objects.all()
    serializer_class = RespondSerializer


class LikeUnlikeView(CreateAPIView):
    """
    This view takes a post and an action on post which can be either like or unlike
    """
    queryset = Post.objects.all()
    serializer_class = LikeUnlikeSerializer
