from django.urls import path
from . import views

app_name = 'mitra'

urlpatterns = [
    path('', views.mitra_dashboard, name='mitra'),
    path('dashboard/', views.mitra_dashboard, name='mitra_dashboard'),
    path('venues/', views.venues_list, name='venues'),
    path('lapangan/', views.lapangan_list, name='lapangan'),
    path('lapangan/<int:lapangan_id>/', views.lapangan_detail, name='lapangan_detail'),
    path('pendapatan/', views.pendapatan, name='pendapatan'),
    path('bookings/', views.bookings, name='bookings'),
]