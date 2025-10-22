from django.urls import path
from main import views

app_name = 'main.admin'

urlpatterns = [
    path('', views.admin_dashboard, name='admin'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]