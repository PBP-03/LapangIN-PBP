from django.shortcuts import render, redirect
from backend.decorators import login_required, anonymous_required, user_required, mitra_required, admin_required

@mitra_required
def mitra_dashboard(request):
    """Mitra dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/mitra.html')