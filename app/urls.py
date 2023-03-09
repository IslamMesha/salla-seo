from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.Test.as_view(), name='index'),
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
]
