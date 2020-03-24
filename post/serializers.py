from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from post.models import Friend, Post
from post.utils import get_friends
from user.models import UserProfile
from weconnect.tasks import send_friend_request_task


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
    likes = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['text', 'image', 'created_at', 'created_by', 'pk', 'custom_list', 'privacy', 'likes', 'liked_by', 'liked_by_me']

    def get_likes(self, obj):
        return obj.liked_by.count()
    
    def get_liked_by(self, obj):
        return [person.get_full_name() for person in obj.liked_by.all()]
    
    def get_liked_by_me(self, obj):
        user = self.context['request'].user
        return Post.objects.filter(pk=obj.pk, liked_by=user).exists()


class SendRequestSerializer(serializers.ModelSerializer):

    username = serializers.CharField(write_only=True)

    class Meta:
        model = Friend
        fields = ['sender', 'receiver', 'username', 'accepted']
        read_only_fields = ['sender', 'receiver']

    def create(self, validated_data):
        sender = self.context['request'].user
        
        try:
            receiver_username = validated_data.pop('username')
            receiver = UserProfile.objects.get(username=receiver_username)
            validated_data['sender'] = sender
            validated_data['receiver'] = receiver
            validated_data['accepted'] = False
            receiver_email = receiver.email
            sender_name = sender.get_full_name()
            send_friend_request_task.delay(receiver_email, sender_name, sender.pk, receiver.pk)
            return super(SendRequestSerializer, self).create(validated_data)

        except UserProfile.DoesNotExist:
            raise NotFound('Username not found')


class RespondSerializer(serializers.ModelSerializer):

    sender = serializers.CharField(write_only=True, source='sender.pk')
    receiver = serializers.CharField(write_only=True, source='receiver.pk')

    class Meta:
        model = Friend
        fields = ['sender', 'receiver', 'accepted']

    def create(self, validated_data):
        sender_pk = validated_data['sender']['pk']
        receiver_pk = validated_data['receiver']['pk']
        accepted = validated_data['accepted']
        try:
            sender = UserProfile.objects.get(pk=sender_pk)
            receiver = UserProfile.objects.get(pk=receiver_pk)

            if accepted:
                obj, created = Friend.objects.get_or_create(sender=sender, receiver=receiver)
                obj.accepted = True
                obj.save()
            else:
                obj = Friend.objects.filter(sender=sender, receiver=receiver).delete()
            return obj
        
        except UserProfile.DoesNotExist:
            raise NotFound("User not found")
            


class LikeUnlikeSerializer(serializers.ModelSerializer):

    action = serializers.CharField(write_only=True)
    pk = serializers.IntegerField(write_only=True)

    class Meta:
        model = Post
        fields = ['liked_by', 'pk', 'action']
        read_only_fields = ['liked_by']

    def create(self, validated_data):
        pk = validated_data.pop('pk')
        action = validated_data.pop('action')
        user = self.context['request'].user
        try:
            post_obj = Post.objects.get(pk=pk)
            liked_by = post_obj.liked_by
            if action == 'like':
                post_obj.liked_by.add(user)
            else:
                post_obj.liked_by.remove(user)
            post_obj.save()
            return post_obj
        except Post.DoesNotExist:
            raise NotFound("Post does not exists")
