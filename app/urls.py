from django.urls import path

from app import views

app_name = 'app'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('Logout/', views.Logout.as_view(), name='logout'),

    path('products/', views.ProductsListAPI.as_view(), name='list_products'),

    path('ask-gpt/', views.AskGPTAboutProductAPI.as_view(), name='ask_gpt'),
    path('salla/submit/', views.SubmitToSallaAPI.as_view(), name='salla_submit'),
    path('prompt/decline/', views.PromptDeclineAPI.as_view(), name='prompt_decline'),
    path('product/history/', views.ProductListHistoryAPI.as_view(), name='product_history'),

    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
    path('webhook/', views.WebhookAPI.as_view(), name='webhook'),
    path('settings/validation/', views.SettingsValidationAPI.as_view(), name='settings_validation'),
    
]
