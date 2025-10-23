from django.shortcuts import render, get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.db.models import Avg
import json

from backend.decorators import login_required, anonymous_required, user_required, mitra_required, admin_required
from backend.models import Venue, VenueImage, VenueFacility, Facility, Court, Review


def venue_list_view(request):
    """Render halaman daftar venue"""
    # Provide a small server-side snapshot of venues so the frontend can render
    # seeded data immediately and avoid falling back to client-only dummy IDs
    # (which produce links like /venue/dummy-1/).
    venues = []
    try:
        qs = Venue.objects.all()[:100]
        for v in qs:
            # pick a safe first image if available
            first_img = ''
            try:
                img = VenueImage.objects.filter(venue=v).order_by('-is_primary', 'id').first()
                if img and img.image_url:
                    first_img = img.image_url
            except Exception:
                first_img = ''

            venues.append({
                'id': str(v.id),
                'name': v.name,
                'category': v.category.name if getattr(v, 'category', None) else '',
                'address': getattr(v, 'address', '') or '',
                'price_per_hour': float(getattr(v, 'price_per_hour', getattr(v, 'price', 0)) or 0),
                'images': [first_img] if first_img else [],
                'avg_rating': 0.0,
                'rating_count': Review.objects.filter(booking__court__venue=v).count(),
            })
    except Exception:
        venues = []

    context = {
        'venues_json': mark_safe(json.dumps(venues, default=str)),
    }
    return render(request, 'venue_list.html', context)


def venue_detail_view(request, venue_id):
    """Render venue detail page"""
    context = {
        'title': 'Detail Venue',
        'is_authenticated': request.user.is_authenticated,
        'venue_id': venue_id
    }
    return render(request, 'venue_detail.html', context)


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