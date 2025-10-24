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

    # Profile management (read / update / delete)
    path('profile/', views.api_profile, name='api_profile'),
    
    # API Mitra URLs - Venues
    path('venues/', views.api_venues, name='api_venues'),
    path('venues/<uuid:venue_id>/', views.api_venue_detail, name='api_venue_detail'),
    
    # API Mitra URLs - Courts
    path('courts/', views.api_courts, name='api_courts'),
    path('courts/<int:court_id>/', views.api_court_detail, name='api_court_detail'),
    path('courts/<int:court_id>/sessions/', views.api_court_sessions, name='api_court_sessions'),
    
    # API Mitra URLs - Pendapatan
    path('pendapatan/', views.api_pendapatan, name='api_pendapatan'),
    
    # API Mitra URLs - Bookings
    path('bookings/', views.api_bookings, name='api_bookings'),
    path('bookings/<uuid:booking_id>/', views.api_booking_detail, name='api_booking_detail'),
    
    # API Utility URLs
    path('sports-categories/', views.api_sports_categories, name='api_sports_categories'),
    
    # API Image Management URLs
    path('venue-images/<int:image_id>/delete/', views.api_delete_venue_image, name='api_delete_venue_image'),
    path('court-images/<int:image_id>/delete/', views.api_delete_court_image, name='api_delete_court_image'),

    # Admin Mitra management
    path('mitra/', views.api_mitra_list, name='api_mitra_list'),
    path('mitra/<uuid:mitra_id>/', views.api_mitra_update_status, name='api_mitra_update_status'),
    path('mitra/<uuid:mitra_id>/venues/', views.api_mitra_venue_details, name='api_mitra_venue_details'),
]