from django.conf.urls import url, include, static
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'user/', include('user.urls'))
]

urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
