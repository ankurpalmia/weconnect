from django.conf.urls import url
from rest_framework import routers

from user.views import (EmailVerifyView, ForgotPasswordView, GetProfileView,
                        GetUserDetails, LoginView, LogoutView,
                        ResetPasswordView, SendForgotPasswordMailView,
                        UserViewset)

router = routers.DefaultRouter()
router.register('signup', UserViewset, basename='signup')

urlpatterns = [
    url(r'login/$', LoginView.as_view()),
    url(r'logout/$', LogoutView.as_view()),
    url(r'getuser/$', GetUserDetails.as_view()),
    url(r'getprofile/$', GetProfileView.as_view()),
    url(r'verify-email/$', EmailVerifyView.as_view()),
    url(r'forgot-password/$', ForgotPasswordView.as_view()),
    url(r'send-forgot-mail/$', SendForgotPasswordMailView.as_view()),
    url(r'reset-password/(?P<pk>\d+)/$', ResetPasswordView.as_view()),
] + router.urls
