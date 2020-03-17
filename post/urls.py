from rest_framework import routers
from django.conf.urls import url
from post.views import PostViewSet, GetPostsView

router = routers.DefaultRouter()
router.register('userpost', PostViewSet, basename='userpost')

urlpatterns = [
    url(r'getposts', GetPostsView.as_view())
] + router.urls
