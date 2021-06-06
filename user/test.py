import hashlib
import json
from datetime import date, datetime

from django.contrib.auth.hashers import check_password, make_password
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from user.models import UserProfile


class SignUpViewTest(TestCase):
    def setUp(self):
        self.user1 = {
            'email': 'ankur@gmail.com',
            'first_name': 'Ankur',
            'username': 'ankur',
            'password': 'asdfghjkl',
            'gender': 'M'
        }
        self.user2 = {
            'email': 'palmia@gmail.com',
            'first_name': 'Palmia',
            'username': 'palmia',
            'password': 'asdfghjkl'
        }

    def test_create_user(self):
        client = APIClient()
        url = reverse('signup-list')
        response = client.post(url, self.user1, format='json')
        self.assertEqual(response.status_code, 201)

    def test_invalid_user(self):
        client = APIClient()
        url = reverse('signup-list')
        response = client.post(url, self.user2, format='json')
        msg = {'gender': ['This field is required.']}
        self.assertEqual(json.loads(response.content), msg)
        self.assertEqual(response.status_code, 400)


class LoginViewTest(TestCase):
    def setUp(self):
        self.user3 = {
            'username': 'ankur',
            'password': 'asdfghjkl'
        }

    def test_user_login(self):
        user = UserProfile.objects.create_user(
            'ankur@gmail.com', 
            'Ankur',
            'ankur',
            )
        user.password = make_password('asdfghjkl')
        user.save()
        client = APIClient()
        url = reverse('login')
        response = client.post(url, self.user3, format='json')
        self.assertEqual(response.status_code, 200)


class EmailVerifyViewTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            'ankur@gmail.com', 
            'Ankur',
            'ankur',
            )
        email = 'ankur@gmail.com'
        email_token = hashlib.md5(email.encode()).hexdigest()
        self.user.password = make_password('asdfghjkl')
        self.user.email_token = email_token
        self.user.save()
        self.url = reverse('verify_email')

    def test_valid_token(self):
        data = {
            'token': str(self.user.email_token)
        }
        client = APIClient()
        response = client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_invalid_token(self):
        client = APIClient()
        data = {
            'token': 'abcdefgh'
        }
        response = client.post(self.url, data, format='json')
        msg = {'detail': 'Not found.'}
        self.assertEqual(json.loads(response.content), msg)
        self.assertEqual(response.status_code, 404)

    def test_user_already_verified(self):
        self.user.verified = True
        self.user.save()
        client = APIClient()
        data = {
            'token': str(self.user.email_token)
        }
        response = client.post(self.url, data, format='json')
        msg = ['Already Verified']
        self.assertEqual(json.loads(response.content), msg)
        self.assertEqual(response.status_code, 400)


class SendForgotMailTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            'ankur@gmail.com', 
            'Ankur',
            'ankur',
            )
        self.url = reverse('send_forgot_mail')
        self.token = hashlib.md5('ankur'.encode()).hexdigest()
        self.client = APIClient()
    
    def test_send_mail_to_valid_username(self):
        data = {
            'username': 'ankur'
        }
        response = self.client.post(self.url, data, format='json')
        msg = {'username': 'ankur', 'forgot_pass_token': self.token}
        self.assertEqual(json.loads(response.content), msg)
        self.assertEqual(response.status_code, 201)
    
    def test_invalid_username(self):
        data = {
            'username': 'user'
        }
        response = self.client.post(self.url, data, format='json')
        msg = {'detail': 'Username not found'}
        self.assertEqual(json.loads(response.content), msg)
        self.assertEqual(response.status_code, 404)
    
    def test_valid_token_received(self):
        data = {
            'username': 'ankur'
        }
        response = self.client.post(self.url, data, format='json')
        url = reverse('forgot_password')
        data = {
            'token': self.token
        }
        response = self.client.post(url, data, format='json')
        msg = {'pk': self.user.pk}
        self.assertEqual(json.loads(response.content), msg)
        self.assertEqual(response.status_code, 201)

    def test_invalid_token_received(self):
        url = reverse('forgot_password')
        data = {
            'token': self.token
        }
        response = self.client.post(url, data, format='json')
        msg = {'detail': 'Not found.'}
        self.assertEqual(json.loads(response.content), msg)
        self.assertEqual(response.status_code, 404)
        