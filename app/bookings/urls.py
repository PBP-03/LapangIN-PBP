from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Bookings Management
    path('', views.api_bookings, name='api_bookings'),
    path('<uuid:booking_id>/', views.api_booking_detail, name='api_booking_detail'),
]
