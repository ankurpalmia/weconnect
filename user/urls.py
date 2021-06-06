from django.conf.urls import url
from rest_framework import routers

from user.views import (EmailVerifyView, ForgotPasswordView, GetProfileView,
                        GetUserDetails, LoginView, LogoutView,
                        ResetPasswordView, SendForgotPasswordMailView,
                        UserViewset)

router = routers.DefaultRouter()
router.register('signup', UserViewset, basename='signup')

urlpatterns = [
    url(r'login/$', LoginView.as_view(), name='login'),
    url(r'logout/$', LogoutView.as_view(), name='logout'),
    url(r'getuser/$', GetUserDetails.as_view(), name='get_user'),
    url(r'getprofile/$', GetProfileView.as_view(), name='get_profile'),
    url(r'verify-email/$', EmailVerifyView.as_view(), name='verify_email'),
    url(r'forgot-password/$', ForgotPasswordView.as_view(), name='forgot_password'),
    url(r'send-forgot-mail/$', SendForgotPasswordMailView.as_view(), name='send_forgot_mail'),
    url(r'(?P<pk>\d+)/reset-password/$', ResetPasswordView.as_view(), name='reset_password'),
] + router.urls
