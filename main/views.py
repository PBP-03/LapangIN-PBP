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
                if img and getattr(img, 'image', None):
                    first_img = img.image.url
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
    """Render halaman detail venue and inject venue data (from DB) as JSON for the frontend.

    The URL may contain a numeric PK or a slug-like string. Try to resolve common cases and
    serialize a small, safe representation of the venue (images, facilities, courts, reviews).
    """
    # Try by primary key first
    venue = None
    try:
        if str(venue_id).isdigit():
            venue = Venue.objects.filter(pk=int(venue_id)).first()
    except Exception:
        venue = None

    # Try slug or exact name match as fallback
    if venue is None:
        try:
            venue = Venue.objects.filter(slug=venue_id).first() if hasattr(Venue, 'slug') else None
        except Exception:
            venue = None

    if venue is None:
        venue = Venue.objects.filter(name__iexact=venue_id).first()

    # If still not found, try interpreting the identifier as a UUID primary key.
    # Many venues in development may be referenced by slug-like strings (e.g. 'dummy-1').
    # Avoid passing non-UUID strings to a UUIDField pk lookup because Django will
    # raise a ValidationError. If it isn't a valid UUID, return 404 instead.
    if venue is None:
        try:
            # Validate UUID format
            import uuid as _uuid
            _uuid.UUID(str(venue_id))
            venue = get_object_or_404(Venue, pk=venue_id)
        except Exception:
            # Not a valid UUID — raise 404 (we already tried slug/name earlier)
            from django.http import Http404
            raise Http404('Venue not found')

    # Images
    images_qs = VenueImage.objects.filter(venue=venue).order_by('-is_primary', 'id')
    images = [img.image.url for img in images_qs if getattr(img, 'image', None)]

    # Facilities
    facilities = []
    for vf in VenueFacility.objects.filter(venue=venue).select_related('facility'):
        f = vf.facility
        facilities.append({
            'name': f.name,
            'icon': f.icon.url if f.icon else None
        })

    # Courts
    courts_qs = Court.objects.filter(venue=venue)
    courts = []
    for c in courts_qs:
        courts.append({'id': c.id, 'name': c.name, 'is_active': c.is_active})

    # Reviews (basic)
    reviews_qs = Review.objects.filter(booking__court__venue=venue).select_related('booking__user')
    reviews = []
    for r in reviews_qs.order_by('-created_at')[:50]:
        user = getattr(r.booking, 'user', None)
        username = ''
        try:
            if user:
                username = getattr(user, 'get_full_name', lambda: None)() or getattr(user, 'username', '')
        except Exception:
            username = getattr(user, 'username', '') if user else ''

        reviews.append({
            'id': r.id,
            'user': username,
            'rating': getattr(r, 'rating', None),
            'date': getattr(r, 'created_at', None).isoformat() if getattr(r, 'created_at', None) else None,
            'comment': getattr(r, 'comment', None),
        })

    avg_rating = reviews_qs.aggregate(avg=Avg('rating'))['avg'] or 0

    # Build serializable dict for the frontend
    venue_data = {
        'id': venue.id,
        'name': venue.name,
        'description': venue.description,
        'category': venue.category.name if getattr(venue, 'category', None) else None,
        'category_icon': venue.category.icon.url if venue.category and venue.category.icon else None,
        'avg_rating': float(avg_rating),
        'rating_count': reviews_qs.count(),
        'address': getattr(venue, 'address', ''),
        'location_url': (
            venue.location_url or 
            (f"https://maps.google.com/?q={venue.address}" if venue.address else 
             f"https://maps.google.com/?q={venue.name}")
        ),
        'contact': getattr(venue, 'contact', ''),
        'number_of_courts': getattr(venue, 'number_of_courts', len(courts)),
        'price_per_hour': float(getattr(venue, 'price_per_hour', getattr(venue, 'price', 0))),
        'images': images,
        'facilities': facilities,
        'courts': courts,
        'reviews': reviews,
    }

    # Ensure safe JSON serialization
    try:
        venue_json = json.dumps(venue_data, default=str)
        print("Venue JSON:", venue_json)  # Debug print
    except Exception as e:
        print("Error serializing venue data:", e)
        venue_json = 'null'
    
    context = {
        'venue_id': venue_id,
        'venue_json': mark_safe(venue_json),
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