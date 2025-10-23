from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import json
from .models import User, ActivityLog, Venue, VenueImage, SportsCategory, Facility, VenueFacility, Court, Review, Booking
from django.db.models import Avg
from .forms import CustomLoginForm, CustomUserCreationForm
from .decorators import login_required, role_required, anonymous_required


# Venue List & Search API
@require_http_methods(["GET"])
def api_venue_list(request):
    """API endpoint for venue list & search/filter"""
    # Get query params
    name = request.GET.get('name')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    location = request.GET.get('location')

    venues = Venue.objects.filter(verification_status='approved')
    if name:
        venues = venues.filter(name__icontains=name)
    if category:
        venues = venues.filter(category__name=category)
    if min_price:
        venues = venues.filter(price_per_hour__gte=min_price)
    if max_price:
        venues = venues.filter(price_per_hour__lte=max_price)
    if location:
        venues = venues.filter(address__icontains=location)

    data = []
    for v in venues:
        images = [img.image.url for img in v.images.all()]
        avg_rating = Review.objects.filter(booking__court__venue=v).aggregate(Avg('rating'))['rating__avg'] or 0
        data.append({
            'id': str(v.id),
            'name': v.name,
            'category': v.category.get_name_display(),
            'category_icon': v.category.icon.url if v.category.icon else None,
            'address': v.address,
            'location_url': v.location_url,
            'contact': v.contact,
            'price_per_hour': float(v.price_per_hour),
            'number_of_courts': v.number_of_courts,
            'images': images,
            'avg_rating': avg_rating,
            'rating_count': Review.objects.filter(booking__court__venue=v).count(),
        })
    return JsonResponse({'status': 'ok', 'data': data})

# Venue Detail API
@require_http_methods(["GET"])
def api_venue_detail(request, venue_id):
    try:
        v = Venue.objects.get(pk=venue_id, verification_status='approved')
    except Venue.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Venue not found'}, status=404)
    images = [img.image.url for img in v.images.all()]
    facilities = [
        {
            'name': vf.facility.name,
            'icon': vf.facility.icon.url if vf.facility.icon else None
        } for vf in VenueFacility.objects.filter(venue=v)
    ]
    courts = [
        {
            'id': c.id,
            'name': c.name,
            'is_active': c.is_active
        } for c in v.courts.all()
    ]
    avg_rating = Review.objects.filter(booking__court__venue=v).aggregate(Avg('rating'))['rating__avg'] or 0
    rating_count = Review.objects.filter(booking__court__venue=v).count()
    reviews = [
        {
            'user': r.booking.user.username,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat() if r.created_at else None
        } for r in Review.objects.filter(booking__court__venue=v).order_by('-created_at')
    ]
    # Bookings for current month
    from datetime import date
    today = date.today()
    first_of_month = today.replace(day=1)
    # last day of month: move to next month then back one day
    if today.month == 12:
        next_month = today.replace(year=today.year+1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month+1, day=1)
    bookings_qs = Booking.objects.filter(booking_date__gte=first_of_month, booking_date__lt=next_month, court__venue=v)
    bookings = [
        {
            'id': b.id,
            'court_id': b.court.id,
            'court_name': b.court.name,
            'user': b.user.username if b.user else None,
            'booking_date': b.booking_date.isoformat() if b.booking_date else None,
            'start_time': b.start_time.isoformat() if b.start_time else None,
            'end_time': b.end_time.isoformat() if b.end_time else None,
            'status': b.booking_status,
        }
        for b in bookings_qs.order_by('booking_date', 'start_time')
    ]
    data = {
        'id': str(v.id),
        'name': v.name,
        'category': v.category.get_name_display(),
        'category_icon': v.category.icon.url if v.category.icon else None,
        'address': v.address,
        'location_url': v.location_url,
        'contact': v.contact,
        'description': v.description,
        'price_per_hour': float(v.price_per_hour),
        'number_of_courts': v.number_of_courts,
        'images': images,
        'facilities': facilities,
        'courts': courts,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'reviews': reviews,
        'bookings': bookings,
    }
    return JsonResponse({'status': 'ok', 'data': data})

# Venue Review List & Create API
@require_http_methods(["GET", "POST"])
@csrf_exempt
def api_venue_reviews(request, venue_id):
    try:
        v = Venue.objects.get(pk=venue_id, verification_status='approved')
    except Venue.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Venue not found'}, status=404)
    if request.method == "GET":
        reviews = [
            {
                'user': r.booking.user.username,
                'rating': r.rating,
                'comment': r.comment,
                'created_at': r.created_at
            } for r in Review.objects.filter(booking__court__venue=v).order_by('-created_at')
        ]
        return JsonResponse({'status': 'ok', 'data': reviews})
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        data = json.loads(request.body)
        rating = data.get('rating')
        comment = data.get('comment')
        court_id = data.get('court_id')
        booking_date = data.get('booking_date')
        # Find booking for this user, court, and date
        try:
            court = Court.objects.get(pk=court_id, venue=v)
            booking = court.booking_set.get(user=request.user, booking_date=booking_date)
        except (Court.DoesNotExist, Booking.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Booking not found'}, status=404)
        if Review.objects.filter(booking=booking).exists():
            return JsonResponse({'status': 'error', 'message': 'Review already exists'}, status=400)
        r = Review.objects.create(booking=booking, rating=rating, comment=comment)
        return JsonResponse({'status': 'ok', 'data': {
            'user': r.booking.user.username,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at
        }})

def index(request):
    return JsonResponse({'status': 'success', 'message': 'Backend API is running'})


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API endpoint for login - for AJAX requests"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': 'Username dan password harus diisi'
            }, status=400)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Log the login activity
            ActivityLog.objects.create(
                user=user,
                action_type='login',
                description=f'User {user.username} logged in via API',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Return user data and redirect URL
            redirect_url = '/'
            if user.role == 'admin':
                redirect_url = '/admin/dashboard'
            elif user.role == 'mitra':
                redirect_url = '/mitra/dashboard'
            
            return JsonResponse({
                'success': True,
                'message': f'Login berhasil! Selamat datang, {user.first_name}',
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'first_name': user.first_name,
                    'role': user.role
                },
                'redirect_url': redirect_url
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Username atau password salah'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Format data tidak valid'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Terjadi kesalahan server'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    """API endpoint for registration - for AJAX requests"""
    try:
        data = json.loads(request.body)
        form = CustomUserCreationForm(data)
        
        if form.is_valid():
            user = form.save()
            
            # Log the registration activity
            ActivityLog.objects.create(
                user=user,
                action_type='create',
                description=f'New user {user.username} registered as {user.role}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Registrasi berhasil! Silakan login.',
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'first_name': user.first_name,
                    'role': user.role
                }
            })
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'message': 'Terjadi kesalahan pada form. Silakan periksa input Anda.',
                'errors': errors
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Format data tidak valid'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Terjadi kesalahan server'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_logout(request):
    """API endpoint for logout - for AJAX requests"""
    try:
        if request.user.is_authenticated:
            # Log the logout activity
            ActivityLog.objects.create(
                user=request.user,
                action_type='logout',
                description=f'User {request.user.username} logged out via API',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logout(request)
            
            return JsonResponse({
                'success': True,
                'message': 'Anda telah berhasil logout.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Anda belum login'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Terjadi kesalahan server'
        }, status=500)


@require_http_methods(["GET"])
def api_user_dashboard(request):
    """API endpoint for user dashboard data"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'user':
        return JsonResponse({
            'success': False,
            'message': 'Access denied'
        }, status=403)
    
    return JsonResponse({
        'success': True,
        'data': {
            'user': {
                'id': str(request.user.id),
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'role': request.user.role
            },
            'title': 'Dashboard User'
        }
    })


@require_http_methods(["GET"])
def api_mitra_dashboard(request):
    """API endpoint for mitra dashboard data"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'mitra':
        return JsonResponse({
            'success': False,
            'message': 'Access denied'
        }, status=403)
    
    # Get mitra's venues
    venues = request.user.venue_set.all()
    venues_data = []
    for venue in venues:
        venues_data.append({
            'id': str(venue.id),
            'name': venue.name,
            'location': venue.location,
            'capacity': venue.capacity,
            'price_per_hour': str(venue.price_per_hour),
            'is_available': venue.is_available
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'user': {
                'id': str(request.user.id),
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'role': request.user.role
            },
            'venues': venues_data,
            'title': 'Dashboard Mitra'
        }
    })


@require_http_methods(["GET"])
def api_admin_dashboard(request):
    """API endpoint for admin dashboard data"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'admin':
        return JsonResponse({
            'success': False,
            'message': 'Access denied'
        }, status=403)
    
    # Get some statistics
    total_users = User.objects.filter(role='user').count()
    total_mitras = User.objects.filter(role='mitra').count()
    recent_activities = ActivityLog.objects.all()[:10]
    
    activities_data = []
    for activity in recent_activities:
        activities_data.append({
            'id': str(activity.id),
            'user': activity.user.username if activity.user else 'Anonymous',
            'action_type': activity.action_type,
            'description': activity.description,
            'timestamp': activity.timestamp.isoformat(),
            'ip_address': activity.ip_address
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'user': {
                'id': str(request.user.id),
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'role': request.user.role
            },
            'statistics': {
                'total_users': total_users,
                'total_mitras': total_mitras
            },
            'recent_activities': activities_data,
            'title': 'Dashboard Admin'
        }
    })


@require_http_methods(["GET"])
def api_user_status(request):
    """API endpoint to check user authentication status"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': str(request.user.id),
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'role': request.user.role
            }
        })
    else:
        return JsonResponse({
            'authenticated': False
        })


def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip