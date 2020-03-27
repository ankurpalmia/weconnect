import hashlib

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from post.models import Friend
from user.models import LoginToken, UserProfile
from weconnect.tasks import send_verify_email_task
from weconnect.tasks import forgot_password_mail_task


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

        return super().create(validated_data)


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
    is_friend = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['username', 'full_name', 'profile_pic', 'date_of_birth', 'gender', 'city', 'is_friend']

    def get_is_friend(self, instance):
        auth_user = self.context['request'].user
        rel = None
        try:
            rel = Friend.objects.get(
                Q(sender=instance, receiver=auth_user) | 
                Q(receiver=instance, sender=auth_user))
            rel = rel.accepted
        except Friend.DoesNotExist:
            rel = None
        return rel


class EmailVerifySerializer(serializers.ModelSerializer):

    token = serializers.CharField(source="email_token", write_only=True)

    class Meta:
        model = UserProfile
        fields = ['token']

    def create(self, validated_data):
        try:
            obj = UserProfile.objects.get(email_token=validated_data['email_token'])
        except UserProfile.DoesNotExist:
            raise NotFound()
        else:
            if obj.verified:
                raise serializers.ValidationError("Already Verified")
            obj.verified = True
            obj.save()
            return obj


class ForgotPasswordSerializer(serializers.ModelSerializer):

    username = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = ['username', 'forgot_pass_token']
        read_only_fields = ['forgot_pass_token']

    def create(self, validated_data):
        try:
            obj = UserProfile.objects.get(username=validated_data['username'])
        except:
            raise NotFound("Username not found")
        else:
            token = hashlib.md5(obj.username.encode()).hexdigest()
            forgot_password_mail_task.delay(obj.email, token)
            obj.forgot_pass_token = token
            obj.save()
            return obj


class CheckPasswordToken(serializers.ModelSerializer):

    token = serializers.CharField(source="forgot_pass_token", write_only=True)

    class Meta:
        model = UserProfile
        fields = ['token', 'pk']
        read_only_fields = ['pk']

    def create(self, validated_data):
        try:
            obj = UserProfile.objects.get(forgot_pass_token=validated_data['forgot_pass_token'])
        except UserProfile.DoesNotExist:
            raise NotFound()
        else:
            obj.forgot_pass_token = ""
            obj.save()
            return obj


class ResetPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['pk', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        instance.password = make_password(validated_data['password'])
        instance.save()
        return instance
        