from django.urls import path
from backend import views as backend_views


app_name = 'main.mitra'

urlpatterns = [
    path('', backend_views.mitra_dashboard, name='mitra'),
]