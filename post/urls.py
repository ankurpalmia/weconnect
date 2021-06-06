from django.conf.urls import url
from rest_framework import routers

from post.views import (GetAllFriendsView, GetPostsView, LikeUnlikeView,
                        PostViewSet, RespondRequest, SendRequestView,
                        UserProfilePostsView)

router = routers.DefaultRouter()
router.register('userpost', PostViewSet, basename='userpost')

urlpatterns = [
    url(r'getposts/$', GetPostsView.as_view(), name='get_feed_posts'),
    url(r'show-profile-posts/$', UserProfilePostsView.as_view(), name='show_profile_posts'),
    url(r'getfriends/$', GetAllFriendsView.as_view(), name='get_friends'),
    url(r'send-request/$', SendRequestView.as_view(), name='send_request'),
    url(r'respond-request/$', RespondRequest.as_view(), name='respond_request'),
    url(r'(?P<pk>\d+)/like-unlike/$', LikeUnlikeView.as_view(), name='like_unlike')
] + router.urls
