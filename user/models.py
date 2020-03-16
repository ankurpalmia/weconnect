import binascii
import os
from datetime import datetime, timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.db import models

from base.models import BaseModel
from weconnect.constants import TOKEN_EXPIRY_TIME, DEFAULT_PROFILE_PIC


class UserManager(BaseUserManager):
    def _create_user(self, email, first_name, username, password, **extra_fields):
        """
        It will create user with entered email and password
        """
        if not email:
            raise ValueError('The given email must be set')
        if not first_name:
            raise ValueError('First Name is mandatory')
        if not username:
            raise ValueError("Users must create a username")

        email = self.normalize_email(email)

        user = self.model(
            email=email, 
            first_name=first_name,
            username=username, 
            **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, username, password=None, **extra_fields):
        extra_fields['is_superuser'] = False
        extra_fields['is_staff'] = False
        return self._create_user(email, first_name, username, password, **extra_fields)

    def create_superuser(self, email, first_name, username, password, **extra_fields):
        extra_fields['is_superuser'] = True
        extra_fields['is_staff'] = True
        return self._create_user(email, first_name, username, password, **extra_fields)


class UserProfile(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    This model stores the User profile related fields
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", default=DEFAULT_PROFILE_PIC)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    city = models.CharField(max_length=50, blank=True)
    verified = models.BooleanField(default=False)
    watched_by = models.ManyToManyField("self", related_name="watching", symmetrical=False, blank=True)
    email_token = models.CharField(max_length=255, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'email']

    objects = UserManager()

    def __str__(self):
        return "{} : {}".format(self.first_name, self.email)

    def get_short_name(self):
        pass

    def get_full_name(self):
        return "{} {}".format(self.first_name, self.last_name)


class LoginToken(BaseModel, models.Model):
    """
    This model will store token which will be used to authenticate user
    """
    key = models.CharField(unique=True, max_length=255, verbose_name="Token Key")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="login_tokens")
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


# class EmailToken(BaseModel, models.Model):
#     """
#     This model will store token which will be used to verify user
#     """
#     key = models.CharField(primary_key=True, max_length=255, verbose_name="Email Token")
#     email = models.EmailField(max_length=100, unique=True)

#     def save(self, *args, **kwargs):
#         if not self.key:
#             self.key = self.generate_key()
#         return super().save(*args, **kwargs)

#     def generate_key(self):
#         return binascii.hexlify(os.urandom(20)).decode()

#     def __str__(self):
#         return "{} : {}".format(self.email, self.key)
