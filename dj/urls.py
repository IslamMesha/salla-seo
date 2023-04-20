from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    # apps
    path('', include('app.urls', namespace='app')),
    path('page/', include('SiteServe.urls', namespace='site_serve')),

    # third party endpoints
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
