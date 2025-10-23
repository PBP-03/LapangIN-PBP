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

    # Venue APIs
    path('venues/', views.api_venue_list, name='api_venue_list'),
    path('venues/<uuid:venue_id>/', views.api_venue_detail, name='api_venue_detail'),
    path('venues/<uuid:venue_id>/reviews/', views.api_venue_reviews, name='api_venue_reviews'),
]