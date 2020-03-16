from user.models import UserProfile, LoginToken
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
import hashlib
from weconnect.tasks import send_verify_email_task
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    """
    This serializer is for user signup
    """
    class Meta:
        model = UserProfile
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'email_token', 'profile_pic', 'verified', 'date_of_birth', 'gender', 'city', 'watched_by', 'pk']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        validated_data['password'] = make_password(password)

        email_token = hashlib.md5(email.encode()).hexdigest()
        validated_data['email_token'] = email_token
        
        send_verify_email_task.delay(email, email_token)

        return super(UserSerializer, self).create(validated_data)
