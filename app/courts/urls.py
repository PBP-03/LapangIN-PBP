from django.urls import path
from . import views

app_name = 'courts'

urlpatterns = [
    # Courts Management
    path('', views.api_courts, name='api_courts'),
    path('<int:court_id>/', views.api_court_detail, name='api_court_detail'),
    path('<int:court_id>/sessions/', views.api_court_sessions, name='api_court_sessions'),
    path('<int:court_id>/sessions/<int:session_id>/', views.api_court_session_detail, name='api_court_session_detail'),

    # Image Management
    path('court-images/<int:image_id>/delete/', views.api_delete_court_image, name='api_delete_court_image'),
]
