from django.urls import include, path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='home'),
    
    # Authentication URLs - now handled by main app views (HTML only)
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    
    # Role-specific dashboard URLs
    path('mitra/', include('main.mitra.urls',"mitra"),name='mitra'),
    path('admin/', include('main.admin.urls',"admin"),name='admin'),

    # Additional dashboard URLs for better UX
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Venue list & detail
    path('lapangan/', views.venue_list_view, name='venue_list'),
    path('venue/<str:venue_id>/', views.venue_detail_view, name='venue_detail'),
]