"""
URL configuration for lapangin project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import views from each app
from app.users import views as users_views
from app.venues import views as venues_views
from app.courts import views as courts_views
from app.bookings import views as bookings_views
from app.reviews import views as reviews_views
from app.revenue import views as revenue_views

urlpatterns = [
    path('admin-django/', admin.site.urls),
    # Include main app URLs
    path('', include('app.main.urls')),
    
    # API endpoints - maintaining old URL structure for compatibility
    # Authentication & Profile (from users app)
    path('api/login/', users_views.api_login, name='api_login'),
    path('api/register/', users_views.api_register, name='api_register'),
    path('api/logout/', users_views.api_logout, name='api_logout'),
    path('api/user-status/', users_views.api_user_status, name='api_user_status'),
    path('api/profile/', users_views.api_profile, name='api_profile'),
    path('api/user-dashboard/', users_views.api_user_dashboard, name='api_user_dashboard'),
    
    # Venues & Sports Categories (from venues app)
    path('api/venues/', venues_views.api_venues, name='api_venues'),
    path('api/venues/<uuid:venue_id>/', venues_views.api_venue_detail, name='api_venue_detail'),
    path('api/public/venues/<uuid:venue_id>/', venues_views.api_venue_detail, name='api_public_venue_detail'),
    path('api/sports-categories/', venues_views.api_sports_categories, name='api_sports_categories'),
    path('api/venue-images/<int:image_id>/delete/', venues_views.api_delete_venue_image, name='api_delete_venue_image'),
    
    # Courts & Sessions (from courts app)
    path('api/courts/', courts_views.api_courts, name='api_courts'),
    path('api/courts/<int:court_id>/', courts_views.api_court_detail, name='api_court_detail'),
    path('api/courts/<int:court_id>/sessions/', courts_views.api_court_sessions, name='api_court_sessions'),
    path('api/court-images/<int:image_id>/delete/', courts_views.api_delete_court_image, name='api_delete_court_image'),
    
    # Bookings & Payments (from bookings app)
    path('api/bookings/', bookings_views.api_bookings, name='api_bookings'),
    path('api/bookings/<uuid:booking_id>/', bookings_views.api_booking_detail, name='api_booking_detail'),
    
    # Reviews (from reviews app)
    path('api/venues/<uuid:venue_id>/reviews/', reviews_views.api_venue_reviews, name='api_venue_reviews'),
    path('api/reviews/<uuid:review_id>/', reviews_views.api_manage_review, name='api_manage_review'),
    
    # Revenue, Dashboards & Admin (from revenue app)
    path('api/pendapatan/', revenue_views.api_pendapatan, name='api_pendapatan'),
    path('api/mitra-dashboard/', revenue_views.api_mitra_dashboard, name='api_mitra_dashboard'),
    path('api/admin-dashboard/', revenue_views.api_admin_dashboard, name='api_admin_dashboard'),
    path('api/mitra/', revenue_views.api_mitra_list, name='api_mitra_list'),
    path('api/mitra/earnings/', revenue_views.api_mitra_earnings, name='api_mitra_earnings'),
    path('api/mitra/<uuid:mitra_id>/', revenue_views.api_mitra_update_status, name='api_mitra_update_status'),
    path('api/mitra/<uuid:mitra_id>/venues/', revenue_views.api_mitra_venue_details, name='api_mitra_venue_details'),
    path('api/mitra/<uuid:mitra_id>/earnings/', revenue_views.api_mitra_earnings_detail, name='api_mitra_earnings_detail'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

