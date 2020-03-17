from rest_framework import routers
from django.conf.urls import url
from user.views import UserViewset, LoginView, LogoutView, GetUserDetails


router = routers.DefaultRouter()
router.register('signup', UserViewset, basename='signup')

urlpatterns = [
    url(r'login/$', LoginView.as_view()),
    url(r'logout/$', LogoutView.as_view()),
    url(r'getuser/$', GetUserDetails.as_view())
] + router.urls
