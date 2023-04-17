from django.urls import path

from app import views

app_name = 'app'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('Logout/', views.Logout.as_view(), name='logout'),

    path('products/', views.ProductsListAPI.as_view(), name='list_products'),

    path('ask-gpt/description/', views.ProductGetDescriptionAPI.as_view(), name='ask_for_description'),
    path('salla/write-description/<str:product_id>/', views.ProductUpdateAPI.as_view(), name='update_descriptions'),
    path('log/descriptions/<str:product_id>/', views.ProductListDescriptionsAPI.as_view(), name='list_descriptions'),

    path('test/', views.Test.as_view(), name='test'),
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
    path('webhook/', views.WebhookAPI.as_view(), name='webhook'),
    path('settings/validation/', views.SettingsValidationAPI.as_view(), name='settings_validation'),
    
]
