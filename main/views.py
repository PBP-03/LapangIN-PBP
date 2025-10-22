from django.shortcuts import render, redirect

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

def login_view(request):
    """Login page - only renders HTML, logic handled by frontend"""
    return render(request, 'auth/login.html')

def register_view(request):
    """Register page - only renders HTML, logic handled by frontend"""  
    return render(request, 'auth/register.html')

def logout_view(request):
    """Logout redirect - actual logout handled by API"""
    return redirect('main:home')

def user_dashboard(request):
    """User dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/user.html')

def mitra_dashboard(request):
    """Mitra dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/mitra.html')

def admin_dashboard(request):
    """Admin dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/admin.html')