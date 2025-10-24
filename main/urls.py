from django.urls import include, path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='home'),
    
    # Authentication URLs - now handled by main app views (HTML only)
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    
    # Role-specific dashboard URLs
    path('mitra/', include(( 'main.mitra.urls', 'main.mitra'), 'main.mitra'), name='mitra'),
    path('admin/', include(( 'main.admin.urls', 'main.admin'), 'main.admin'), name='admin'),
    # Direct route to admin mitra page (convenience name 'admin')
    path('admin/mitra/', views.admin_mitra_page, name='admin'),

    # Additional dashboard URLs for better UX
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.profile_view, name='profile'),
]