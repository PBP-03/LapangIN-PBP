from django.urls import path
from . import views

app_name = 'revenue'

urlpatterns = [
    # Revenue/Pendapatan Management
    path('pendapatan/', views.api_pendapatan, name='api_pendapatan'),
    
    # Dashboards
    path('mitra-dashboard/', views.api_mitra_dashboard, name='api_mitra_dashboard'),
    path('admin-dashboard/', views.api_admin_dashboard, name='api_admin_dashboard'),
    
    # Admin Mitra Management
    path('mitra/', views.api_mitra_list, name='api_mitra_list'),
    path('mitra/<uuid:mitra_id>/', views.api_mitra_update_status, name='api_mitra_update_status'),
    path('mitra/<uuid:mitra_id>/venues/', views.api_mitra_venue_details, name='api_mitra_venue_details'),
]
