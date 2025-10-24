from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Note: These are mounted at /api/ level in main urls.py
    # So /api/login/ maps to views.api_login
    path('', views.api_login, name='api_login'),  # For /api/login/
]
