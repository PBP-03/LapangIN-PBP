from django.urls import include, path
from . import views
from backend import views as backend_views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='home'),
    
    # Authentication URLs - now handled by main app views (HTML only)
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    
    # Role-specific dashboard URLs
    path('mitra/', include('main.mitra.urls',"mitra"),name='mitra'),
    # Admin sub-routes (dashboard and admin-specific pages)
    path('admin/mitra/', backend_views.admin_mitra_page, name='admin_mitra_page'),
    path('admin/', include('main.admin.urls',"admin"),name='admin'),

    # Additional dashboard URLs for better UX
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]