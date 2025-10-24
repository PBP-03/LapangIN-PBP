from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.safestring import mark_safe
from django.db.models import Avg
import json

from app.users.decorators import login_required, anonymous_required, user_required, mitra_required, admin_required
from app.venues.models import Venue, VenueImage, VenueFacility, Facility, OperationalHour
from app.courts.models import Court
from app.reviews.models import Review
from app.bookings.models import Booking


@admin_required
def admin_mitra_earnings_page(request):
    """Render the admin mitra earnings dashboard page."""
    return render(request, 'dashboard/admin_mitra_earnings.html')



def venue_list_view(request):
    """Render halaman daftar venue"""
    # Don't send initial data, let JavaScript fetch from API with pagination
    venues = []
    try:
        # Only send first page for initial load - filter for approved venues only
        qs = Venue.objects.filter(verification_status='approved').order_by('-created_at', 'name')[:9]
        print(f"[Initial Load] Found {Venue.objects.filter(verification_status='approved').count()} approved venues")
        print(f"[Initial Load] Showing first {qs.count()} venues")
        for v in qs:
            # pick a safe first image if available
            first_img = ''
            try:
                img = VenueImage.objects.filter(venue=v).order_by('-is_primary', 'id').first()
                if img and img.image_url:
                    first_img = img.image_url
            except Exception as e:
                print(f"Error getting image for venue {v.name}: {e}")
                first_img = ''

            # Calculate average rating
            avg_rating = Review.objects.filter(booking__court__venue=v).aggregate(Avg('rating'))['rating__avg'] or 0.0
            rating_count = Review.objects.filter(booking__court__venue=v).count()
            
            # Get all unique categories from courts in this venue
            courts = Court.objects.filter(venue=v).select_related('category')
            categories = set()
            for court in courts:
                if court.category:
                    categories.add(court.category.get_name_display())
            categories_display = ', '.join(sorted(categories)) if categories else ''
            
            venues.append({
                'id': str(v.id),
                'name': v.name,
                'category': categories_display,
                'address': getattr(v, 'address', '') or '',
                'price_per_hour': float(Court.objects.filter(venue=v).aggregate(Avg('price_per_hour'))['price_per_hour__avg'] or 0),
                'images': [first_img] if first_img else [],
                'avg_rating': round(avg_rating, 1),
                'rating_count': rating_count,
            })
            print(f"[Initial Load] Added venue: {v.name} (ID: {v.id})")
    except Exception as e:
        print(f"Error in venue_list_view: {e}")
        import traceback
        traceback.print_exc()
        venues = []
    print(f"[Initial Load] Total venues loaded: {len(venues)}")
    venue_names = [v['name'] for v in venues]
    print(f"[Initial Load] Venue names: {venue_names}")
    context = {
        'venues_json': mark_safe(json.dumps(venues, default=str)),
    }
    return render(request, 'venue_list.html', context)


def venue_detail_view(request, venue_id):
    """Render venue detail page with complete information"""
    from datetime import datetime, date
    
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
    
    # Get today's date to check session availability
    today = date.today()
    
    # For each court, get session availability for today
    courts_with_availability = []
    for court in courts:
        court_data = {
            'id': court.id,
            'name': court.name,
            'category': court.category,
            'price_per_hour': court.price_per_hour,
            'sessions': []
        }
        
        # Get all sessions for this court
        sessions = court.sessions.all()
        for session in sessions:
            # Check if this session is booked for today
            is_booked = Booking.objects.filter(
                court=court,
                session=session,
                booking_date=today,
                booking_status__in=['pending', 'confirmed']
            ).exists()
            
            # Calculate duration in minutes
            start_datetime = datetime.combine(today, session.start_time)
            end_datetime = datetime.combine(today, session.end_time)
            duration_minutes = int((end_datetime - start_datetime).total_seconds() / 60)
            
            session_data = {
                'id': str(session.id),
                'session_name': session.session_name,
                'start_time': session.start_time.strftime('%H:%M'),
                'end_time': session.end_time.strftime('%H:%M'),
                'duration': duration_minutes,
                'is_available': not is_booked
            }
            court_data['sessions'].append(session_data)
        
        courts_with_availability.append(court_data)
    
    # Convert courts data to JSON for JavaScript
    import json
    courts_json = json.dumps(courts_with_availability, default=str)
    
    context = {
        'title': venue.name,
        'venue': venue,
        'courts': courts_with_availability,
        'courts_json': courts_json,
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


@admin_required
def admin_mitra_page(request):
    """Convenience route to the admin mitra management page."""
    # reuse the admin sub-app view
    return render(request, 'dashboard/admin_mitra.html')

@login_required
def profile_view(request):
    return render(request, 'profile.html')

def about_view(request):
    """About page"""
    return render(request, 'about.html')

def contact_view(request):
    """Contact page"""
    return render(request, 'contact.html')

def daftar_mitra_view(request):
    """Daftar Mitra page"""
    return render(request, 'daftar_mitra.html')

@login_required
def booking_checkout_view(request):
    """Booking checkout page"""
    return render(request, 'booking_checkout.html')

@login_required  
def booking_history_view(request):
    """Booking history page"""
    return render(request, 'booking_history.html')
