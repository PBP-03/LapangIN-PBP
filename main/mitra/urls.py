from django.urls import path
from . import views

app_name = 'main.mitra'

urlpatterns = [
    path('', views.mitra_dashboard, name='mitra'),
    path('dashboard/', views.mitra_dashboard, name='mitra_dashboard'),
    path('venues/', views.venues_list, name='venues'),
    path('courts/', views.courts_list, name='courts'),
    path('pendapatan/', views.pendapatan, name='pendapatan'),
    path('bookings/', views.bookings, name='bookings'),
]