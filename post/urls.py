from rest_framework import routers
from django.conf.urls import url
from post.views import PostViewSet, GetPostsView, UserProfileView, GetAllFriendsView

router = routers.DefaultRouter()
router.register('userpost', PostViewSet, basename='userpost')

urlpatterns = [
    url(r'getposts/$', GetPostsView.as_view()),
    url(r'showprofile/$', UserProfileView.as_view()),
    url(r'getfriends/$', GetAllFriendsView.as_view())
] + router.urls
