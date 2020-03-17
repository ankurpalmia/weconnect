from user.models import UserProfile
from post.models import Post, Friend
from rest_framework import serializers
from post.utils import get_friends
from django.db.models import Q


class PostSerializer(serializers.ModelSerializer):
    """
    This serializer is for users' posts
    """
    class Meta:
        model = Post
        fields = ['text', 'image', 'created_by', 'privacy', 'custom_list', 'liked_by']


class GetPostSerializer(serializers.ModelSerializer):
    """
    This serializer will get all posts for a user's feed
    """
    class Meta:
        model = UserProfile
        fields = ['username']
    
    def to_representation(self, instance):
        all_friends = get_friends(instance)
        all_posts = Post.objects.filter(created_by=instance)
        for friend in all_friends:
            posts = Post.objects.filter(
                Q(created_by=friend, privacy='PUBLIC') | 
                Q(created_by=friend, privacy='FRIENDS'))
            all_posts |= posts
        custom_list_posts = instance.post_by_friends.all()
        all_posts |= custom_list_posts
        all_posts = all_posts.order_by('-created_at')
        post_list = []
        for post in all_posts:
            post_list.append({
                'text': post.text,
                'image': post.image if post.image else None,
                'created_by': {
                    'name': post.created_by.get_full_name(),
                    'username': post.created_by.username
                },
                'likes': post.liked_by.count(),
                'liked_by': [person.get_full_name() for person in post.liked_by.all()],
                'created_at': post.created_at
            })
        all_posts = post_list
        post_list = super().to_representation(instance)
        post_list['posts'] = all_posts
        return post_list
    