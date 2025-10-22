from django.shortcuts import render
from backend.decorators import  mitra_required

@mitra_required
def mitra_dashboard(request):
    """Mitra dashboard page - only renders HTML, data fetched via API"""
    return render(request, 'dashboard/mitra.html')