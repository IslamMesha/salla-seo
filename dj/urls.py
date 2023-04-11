from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # apps
    path('', include('app.urls', namespace='app')),
    path('page/', include('SiteServe.urls', namespace='site_serve')),

    # third party endpoints
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
]
