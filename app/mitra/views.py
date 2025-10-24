from django.shortcuts import render
from app.backend.decorators import mitra_required

@mitra_required
def mitra_dashboard(request):
    """Mitra dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/mitra.html')


@mitra_required
def venues_list(request):
    """Venues list page - only renders HTML, data fetched via API"""
    return render(request, 'mitra/venues.html')


@mitra_required
def lapangan_list(request):
    """Lapangan list page - only renders HTML, data fetched via API"""
    return render(request, 'mitra/lapangan.html')


@mitra_required
def pendapatan(request):
    """Pendapatan/Revenue page - only renders HTML, data fetched via API"""
    return render(request, 'mitra/pendapatan.html')


@mitra_required
def bookings(request):
    """Bookings management page - only renders HTML, data fetched via API"""
    return render(request, 'mitra/bookings.html')


@mitra_required
def lapangan_detail(request, lapangan_id):
    """Lapangan detail page - only renders HTML, data fetched via API"""
    return render(request, 'mitra/lapangan_detail.html', {'lapangan_id': lapangan_id})
