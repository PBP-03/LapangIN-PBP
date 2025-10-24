from django.urls import include, path
from . import views

app_name = 'main'

urlpatterns = [
    
    path('', views.index, name='home'),
    
    # Authentication URLs - now handled by main app views (HTML only)
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    
    # Role-specific dashboard URLs
    path('mitra/', include(( 'app.mitra.urls', 'app.mitra'), 'app.mitra'), name='mitra'),
    path('admin/', include(( 'app.admin.urls', 'app.admin'), 'app.admin'), name='admin'),
    # Direct route to admin mitra page (convenience name 'admin')
    path('admin/mitra/', views.admin_mitra_page, name='admin'),
    # Route for admin mitra earnings view
    path('admin/mitra/earnings/', views.admin_mitra_earnings_page, name='admin_mitra_earnings'),

    # Additional dashboard URLs for better UX
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Venue list & detail
    path('lapangan/', views.venue_list_view, name='venue_list'),
    path('lapangan/<str:venue_id>/', views.venue_detail_view, name='venue_detail'),
    
    # Booking checkout
    path('booking/checkout/', views.booking_checkout_view, name='booking_checkout'),
    path('booking-history/', views.booking_history_view, name='booking_history'),
    
    path('profile/', views.profile_view, name='profile'),
]