from rest_framework import routers
from django.conf.urls import url
from user.views import UserViewset


router = routers.DefaultRouter()
router.register('signup', UserViewset, basename='signup')

urlpatterns = [
] + router.urls
