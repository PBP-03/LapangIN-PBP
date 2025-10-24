from django.urls import path
from . import views

app_name = 'main.admin'

urlpatterns = [
    path('', views.admin_dashboard, name='admin'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('mitra/', views.admin_mitra, name='admin_mitra'),
]