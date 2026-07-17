from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    # Venues Management
    path('', views.api_venues, name='api_venues'),
    path('<uuid:venue_id>/', views.api_venue_detail, name='api_venue_detail'),
    path('public/<uuid:venue_id>/', views.api_venue_detail, name='api_public_venue_detail'),
    
    # Sports Categories
    path('sports-categories/', views.api_sports_categories, name='api_sports_categories'),
    
    # Image Management
    path('venue-images/<int:image_id>/delete/', views.api_delete_venue_image, name='api_delete_venue_image'),
    
    # Operational Hours
    path('<uuid:venue_id>/operational-hours/', views.api_venue_operational_hours, name='api_venue_operational_hours'),
    path('<uuid:venue_id>/operational-hours/<int:hour_id>/', views.api_venue_operational_hour_detail, name='api_venue_operational_hour_detail'),
]
