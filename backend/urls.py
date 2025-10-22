from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('', views.index, name='index'),
    
    # Authentication URLs
    path('login/', views.api_login, name='api_login'),
    
    # Dashboard URLs  
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('mitra-dashboard/', views.mitra_dashboard, name='mitra_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]