from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from django.db.models import Avg
from urllib.parse import unquote
import requests
import json

from app.users.decorators import login_required, anonymous_required, user_required, mitra_required, admin_required
from app.venues.models import Venue, VenueImage, VenueFacility, Facility, OperationalHour
from app.courts.models import Court
from app.reviews.models import Review
from app.bookings.models import Booking


def venue_list_view(request):
    """Render halaman daftar venue"""
    # Don't send initial data, let JavaScript fetch from API with pagination
    venues = []
    search_query = request.GET.get('search', '').strip()
    
    try:
        # Filter for approved venues only
        qs = Venue.objects.filter(verification_status='approved')
        
        # Apply search filter if search query exists
        if search_query:
            from django.db.models import Q
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            print(f"[Search] Searching for: '{search_query}'")
            print(f"[Search] Found {qs.count()} matching venues")
        
        # Order and limit results
        qs = qs.order_by('-created_at', 'name')[:9]
        
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
        'search_query': search_query,
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
    
    # Get venue reviews with pagination
    from django.core.paginator import Paginator
    all_reviews = Review.objects.filter(booking__court__venue=venue).select_related('booking__user').order_by('-created_at')
    avg_rating = all_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(all_reviews, 5)  # Show 5 reviews per page
    reviews = paginator.get_page(page_number)
    
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
        'review_count': all_reviews.count(),
        'is_authenticated': request.user.is_authenticated,
        'can_review': can_review,
        'today': today.isoformat()
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


@csrf_exempt
@require_http_methods(["GET"])
def proxy_image(request):
    """Proxy external images to bypass CORS"""
    image_url = unquote(request.GET.get('url', ''))
    
    if not image_url or not image_url.startswith(('http://', 'https://')):
        return JsonResponse({'error': 'Invalid URL'}, status=400)
    
    try:
        response = requests.get(image_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            http_response = HttpResponse(response.content, content_type=response.headers.get('Content-Type', 'image/jpeg'))
            http_response['Access-Control-Allow-Origin'] = '*'
            http_response['Cache-Control'] = 'public, max-age=86400'
            return http_response
        return JsonResponse({'error': f'Failed: {response.status_code}'}, status=response.status_code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
