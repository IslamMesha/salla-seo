from django.urls import path

from SiteServe import views

app_name = 'site_serve'

urlpatterns = [
    path('<str:slug>/', views.LoadStaticPageView.as_view(), name='page'),
]