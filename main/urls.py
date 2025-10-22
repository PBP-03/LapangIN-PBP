from django.urls import include, path
from . import views
from backend import views as backend_views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    
    # Authentication URLs
    path('login/', backend_views.login_view, name='login'),
    path('register/', backend_views.register_view, name='register'),
    path('logout/', backend_views.logout_view, name='logout'),
    
    # Role-specific dashboard URLs
    path('mitra/', include('main.mitra.urls')),
    path('master/', include('main.admin.urls')),

    # Additional dashboard URLs for better UX
    path('mitra-dashboard/', backend_views.mitra_dashboard, name='mitra_dashboard'),
    path('admin-dashboard/', backend_views.admin_dashboard, name='admin_dashboard'),
    path('user-dashboard/', backend_views.user_dashboard, name='user_dashboard'),
]