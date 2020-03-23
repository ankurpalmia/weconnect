from django.conf.urls import url
from rest_framework import routers

from post.views import (GetAllFriendsView, GetPostsView, LikeUnlikeView,
                        PostViewSet, RespondRequest, SendRequestView,
                        UserProfilePostsView)

router = routers.DefaultRouter()
router.register('userpost', PostViewSet, basename='userpost')

urlpatterns = [
    url(r'getposts/$', GetPostsView.as_view()),
    url(r'show-profile-posts/$', UserProfilePostsView.as_view()),
    url(r'getfriends/$', GetAllFriendsView.as_view()),
    url(r'send-request/$', SendRequestView.as_view()),
    url(r'respond-request/$', RespondRequest.as_view()),
    url(r'like-unlike/$', LikeUnlikeView.as_view())
] + router.urls
