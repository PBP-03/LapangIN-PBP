from django.shortcuts import render
from backend.decorators import mitra_required

@mitra_required
def mitra_dashboard(request):
    """Mitra dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/mitra.html')


@mitra_required
def venues_list(request):
    """Venues list page - only renders HTML, data fetched via API"""
    return render(request, 'mitra/venues.html')


@mitra_required
def courts_list(request):
    """Courts list page - only renders HTML, data fetched via API"""
    return render(request, 'mitra/courts.html')


@mitra_required
def pendapatan(request):
    """Pendapatan/Revenue page - only renders HTML, data fetched via API"""
    return render(request, 'mitra/pendapatan.html')


@mitra_required
def bookings(request):
    """Bookings management page - only renders HTML, data fetched via API"""
    return render(request, 'mitra/bookings.html')
