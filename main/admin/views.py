from django.shortcuts import render
from backend.decorators import admin_required

@admin_required
def admin_dashboard(request):
    """Admin dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/admin.html')