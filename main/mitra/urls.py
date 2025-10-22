from django.urls import path
from . import views

app_name = 'main.mitra'

urlpatterns = [
    path('', views.mitra_dashboard, name='mitra'),
    path('dashboard/', views.mitra_dashboard, name='mitra_dashboard'),
]