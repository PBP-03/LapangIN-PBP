from django.shortcuts import render
from app.users.decorators import admin_required

@admin_required
def admin_dashboard(request):
    """Admin dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/admin.html')


@admin_required
def admin_mitra(request):
    """Admin page to manage mitra - renders HTML template which talks to JSON API"""
    return render(request, 'dashboard/admin_mitra.html')


@admin_required
def admin_mitra_earnings(request):
    """Admin page to view mitra earnings - renders HTML template which talks to JSON API"""
    return render(request, 'dashboard/admin_mitra_earnings.html')