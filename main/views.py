from django.shortcuts import render, get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.db.models import Avg
import json

from backend.decorators import login_required, anonymous_required, user_required, mitra_required, admin_required
from backend.models import (
    Venue, VenueImage, VenueFacility, Facility, 
    Court, Review, OperationalHour, Booking
)


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
                'price_per_hour': float(Court.objects.filter(venue=v).aggregate(Avg('price_per_hour'))['price_per_hour__avg'] or 0),
                'images': [first_img] if first_img else [],
                'avg_rating': 0.0,
                'rating_count': Review.objects.filter(booking__court__venue=v).count(),
            })
    except Exception:
        venues = []
    print(venues)
    context = {
        'venues_json': mark_safe(json.dumps(venues, default=str)),
    }
    return render(request, 'venue_list.html', context)


def venue_detail_view(request, venue_id):
    """Render venue detail page with complete information"""
    venue = get_object_or_404(Venue, id=venue_id)
    
    # Get all courts for this venue with their sessions
    courts = Court.objects.filter(venue=venue).prefetch_related('sessions')
    
    # Get venue facilities
    facilities = VenueFacility.objects.filter(venue=venue).select_related('facility')
    
    # Get venue images
    images = VenueImage.objects.filter(venue=venue).order_by('-is_primary')
    
    # Get operational hours
    operational_hours = OperationalHour.objects.filter(venue=venue).order_by('day_of_week')
    
    # Get venue reviews
    reviews = Review.objects.filter(booking__court__venue=venue).select_related('booking__user')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if user has completed booking at this venue (eligible to review)
    can_review = False
    if request.user.is_authenticated:
        can_review = Booking.objects.filter(
            court__venue=venue,
            user=request.user,
            booking_status='completed'
        ).exclude(
            review__isnull=False  # Exclude bookings that already have reviews
        ).exists()
    
    context = {
        'title': venue.name,
        'venue': venue,
        'courts': courts,
        'facilities': facilities,
        'images': images,
        'operational_hours': operational_hours,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_count': reviews.count(),
        'is_authenticated': request.user.is_authenticated,
        'can_review': can_review
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