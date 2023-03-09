from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # apps
    path('', include('app.urls', namespace='app')),

    # third party endpoints
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
]
