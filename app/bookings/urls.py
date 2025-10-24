from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Bookings Management
    path('', views.api_bookings, name='api_bookings'),
    path('create/', views.create_booking, name='create_booking'),
    path('history/', views.api_user_booking_history, name='user_booking_history'),
    path('<uuid:booking_id>/', views.api_booking_detail, name='api_booking_detail'),
    
    # Booking Cancellation
    path('<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('<uuid:booking_id>/status/', views.get_booking_status, name='booking_status'),
]
