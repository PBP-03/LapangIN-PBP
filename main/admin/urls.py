from django.urls import path
from backend import views as backend_views


app_name = 'main.admin'

urlpatterns = [
    path('', backend_views.admin_dashboard, name='admin'),
    path('dashboard/', backend_views.admin_dashboard, name='admin_dashboard'),
]