from rest_framework.permissions import BasePermission
from post.models import Post
from django.shortcuts import get_object_or_404


class IsVerifiedOwner(BasePermission):
    """
    Defining custom permission:
    States that the user is verified and is the owner of the post
    """
    def has_permission(self, request, view):
        if view.kwargs:
            post_id = view.kwargs['pk']
            post_obj = get_object_or_404(Post, id=post_id)
            return post_obj.created_by == request.user and request.user.verified
        return bool(request.user.verified)
