from user.models import UserProfile, LoginToken
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
import hashlib
from django.contrib.auth import authenticate
from post.models import Friend
from weconnect.tasks import send_verify_email_task
from django.db.models import Q


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer is for user signup
    """
    full_name = serializers.CharField(source='get_full_name', required=False)

    class Meta:
        model = UserProfile
        fields = ['email', 'username', 'full_name', 'first_name', 'last_name', 'password', 'email_token', 'profile_pic', 'verified', 'date_of_birth', 'gender', 'city', 'watched_by', 'pk']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        validated_data['password'] = make_password(password)

        email_token = hashlib.md5(email.encode()).hexdigest()
        validated_data['email_token'] = email_token

        send_verify_email_task.delay(email, email_token)

        return super(UserSerializer, self).create(validated_data)


class LoginSerializer(serializers.Serializer):
    """
    This serializer is for user Login
    """
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=100)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                msg = ('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = ('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    This serializer is used for User Profile
    """
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = UserProfile
        fields = ['username', 'full_name', 'profile_pic', 'date_of_birth', 'gender', 'city']

    def to_representation(self, instance):
        user = super().to_representation(instance)
        auth_user = self.context['request'].user
        is_friend = None
        try:
            is_friend = Friend.objects.get(
                Q(sender=instance, receiver=auth_user) | 
                Q(receiver=instance, sender=auth_user))
            is_friend = is_friend.accepted
        except Friend.DoesNotExist:
            is_friend = None
        user['is_friend'] = is_friend
        return user

        