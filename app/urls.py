from django.urls import path

from app import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.ProductsListAPI.as_view(), name='list_products'),
    path('test/', views.Test.as_view(), name='test'),
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
]
