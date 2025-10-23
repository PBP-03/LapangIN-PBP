from django.shortcuts import render, redirect
from backend.decorators import login_required, anonymous_required, user_required, mitra_required, admin_required, role_required

def index(request):
    return render(request, 'index.html')

@anonymous_required('/dashboard')
def login_view(request):
    """Login page - only renders HTML, logic handled by frontend"""
    return render(request, 'auth/login.html')

@anonymous_required('/dashboard')
def register_view(request):
    """Register page - only renders HTML, logic handled by frontend"""  
    return render(request, 'auth/register.html')


@user_required
def user_dashboard(request):
    """User dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/user.html')

@login_required
def profile_view(request):
    return render(request, 'profile.html')