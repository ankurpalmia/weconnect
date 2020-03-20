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
        fields = ['text', 'image', 'created_by', 'privacy', 'custom_list', 'liked_by', 'pk']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super(PostSerializer, self).create(validated_data)


class UserForPost(serializers.ModelSerializer):
    """
    This serializer is for serializing user related fields for PostSerializer
    """
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = UserProfile
        fields = ['username', 'full_name', 'profile_pic', 'pk']


class GetPostSerializer(serializers.ModelSerializer):
    """
    This serializer will get all posts for a user's feed
    """
    created_by = UserForPost(read_only=True)

    class Meta:
        model = Post
        fields = ['text', 'image', 'created_at', 'created_by', 'pk', 'custom_list', 'privacy']
    
    def to_representation(self, instance):
        post_list = super().to_representation(instance)
        post_list['likes'] = instance.liked_by.count()
        post_list['liked_by'] = [person.get_full_name() for person in instance.liked_by.all()]
        post_list['liked_by_me'] = UserProfile.objects.filter(liked_posts=post_list['pk']).exists()
        return post_list
