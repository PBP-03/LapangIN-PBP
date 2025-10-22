from django.urls import include, path
from . import views
from backend import views as backend_views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='home'),
    
    # Authentication URLs
    path('login/', backend_views.login_view, name='login'),
    path('register/', backend_views.register_view, name='register'),
    path('logout/', backend_views.logout_view, name='logout'),
    
    # Role-specific dashboard URLs
    path('mitra/', include('main.mitra.urls',"mitra"),name='mitra'),
    path('admin/', include('main.admin.urls',"admin"),name='admin'),

    # Additional dashboard URLs for better UX
    path('dashboard/', backend_views.user_dashboard, name='user_dashboard'),
]