from django.contrib import admin
from user.models import UserProfile, LoginToken

admin.site.register(UserProfile)
admin.site.register(LoginToken)
