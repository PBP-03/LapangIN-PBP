from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Reviews Management
    path('venues/<uuid:venue_id>/reviews/', views.api_venue_reviews, name='api_venue_reviews'),
    path('<uuid:review_id>/', views.api_manage_review, name='api_manage_review'),
]
