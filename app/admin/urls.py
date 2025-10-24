from django.urls import path
from . import views

app_name = 'app.admin'

urlpatterns = [
    path('', views.admin_dashboard, name='admin'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('mitra/', views.admin_mitra, name='admin_mitra'),
    path('mitra/earnings/', views.admin_mitra_earnings, name='admin_mitra_earnings'),
]