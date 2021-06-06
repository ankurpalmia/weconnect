from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'user/', include('user.urls')),
    url(r'post/', include('post.urls'))
]

urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
