from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('', views.index, name='index'),
    
    # API Authentication URLs
    path('login/', views.api_login, name='api_login'),
    path('register/', views.api_register, name='api_register'),
    path('logout/', views.api_logout, name='api_logout'),
    path('user-status/', views.api_user_status, name='api_user_status'),
    
    # API Dashboard URLs  
    path('user-dashboard/', views.api_user_dashboard, name='api_user_dashboard'),
    path('mitra-dashboard/', views.api_mitra_dashboard, name='api_mitra_dashboard'),
    path('admin-dashboard/', views.api_admin_dashboard, name='api_admin_dashboard'),
    
    # Mitra API endpoints (mounted under project as /api/mitra/)
    path('mitra/', views.mitra_list, name='mitra_list'),
    path('mitra/<int:pk>/', views.mitra_detail, name='mitra_detail'),
    # Legacy-style names requested by asdos
    path('mitra_list/', views.mitra_list, name='mitra_list_alt'),
    path('mitra_detail/<int:pk>/', views.mitra_detail, name='mitra_detail_alt'),
    
    # API-level admin path should redirect to the HTML admin page (project-level)
    path('admin/mitra/', views.api_admin_mitra_redirect, name='api_admin_mitra_redirect'),
]