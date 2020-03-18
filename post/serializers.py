from user.models import UserProfile
from post.models import Post, Friend
from rest_framework import serializers
from post.utils import get_friends, create_post_dict
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
        all_posts = create_post_dict(all_posts)
        post_list = super().to_representation(instance)
        post_list['posts'] = all_posts
        return post_list
