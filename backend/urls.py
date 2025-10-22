from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('', views.index, name='index'),
    
    # API Authentication URLs
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/user-status/', views.api_user_status, name='api_user_status'),
    
    # Dashboard URLs  
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('mitra-dashboard/', views.mitra_dashboard, name='mitra_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]