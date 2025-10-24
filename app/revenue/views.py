from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.db.models import Sum, Count, Q, Avg
from decimal import Decimal
import json
from datetime import date

# Import models from new apps
from app.users.models import User
from app.venues.models import Venue, SportsCategory, VenueFacility
from app.courts.models import Court, CourtSession
from app.bookings.models import Booking, Payment
from app.reviews.models import Review
from app.revenue.models import Pendapatan, ActivityLog
# API: Mitra Earnings Summary
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
@csrf_exempt
def api_mitra_earnings(request):
    """Return each mitra's total earnings based on completed transactions (paid)."""
    if not request.user.is_authenticated or request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)

    mitras = User.objects.filter(role='mitra')
    data = []
    for mitra in mitras:
        # Sum net_amount for Pendapatan where payment_status is 'paid' and booking_status is 'completed'
        total_earnings = Pendapatan.objects.filter(
            mitra=mitra,
            payment_status='paid',
            booking__booking_status='completed'
        ).aggregate(total=Sum('net_amount'))['total'] or 0
        
        # Count completed transactions
        completed_transactions = Pendapatan.objects.filter(
            mitra=mitra,
            payment_status='paid',
            booking__booking_status='completed'
        ).count()
        
        data.append({
            'mitra_id': str(mitra.id),
            'mitra_name': mitra.get_full_name() or mitra.username,
            'mitra_email': mitra.email,
            'mitra_phone': mitra.phone_number or '-',
            'total_earnings': float(total_earnings),
            'completed_transactions': completed_transactions
        })
    return JsonResponse({'status': 'ok', 'data': data})


@require_http_methods(["GET"])
@csrf_exempt
def api_mitra_earnings_detail(request, mitra_id):
    """Get detailed earnings and transaction information for a specific mitra"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    try:
        mitra = User.objects.get(id=mitra_id, role='mitra')
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Mitra not found'}, status=404)
    
    # Get all completed and paid transactions for this mitra
    pendapatans = Pendapatan.objects.filter(
        mitra=mitra,
        payment_status='paid',
        booking__booking_status='completed'
    ).select_related('booking', 'booking__user', 'booking__court', 'booking__court__venue').order_by('-created_at')
    
    transactions = []
    total_earnings = 0
    total_commission = 0
    
    for p in pendapatans:
        total_earnings += float(p.net_amount)
        total_commission += float(p.commission_amount)
        
        transactions.append({
            'id': str(p.id),
            'booking_id': str(p.booking.id),
            'customer_name': p.booking.user.get_full_name() or p.booking.user.username,
            'venue_name': p.booking.court.venue.name,
            'court_name': p.booking.court.name,
            'booking_date': p.booking.booking_date.isoformat(),
            'time_slot': f"{p.booking.start_time.strftime('%H:%M')} - {p.booking.end_time.strftime('%H:%M')}",
            'amount': float(p.amount),
            'commission_rate': float(p.commission_rate),
            'commission_amount': float(p.commission_amount),
            'net_amount': float(p.net_amount),
            'paid_at': p.paid_at.isoformat() if p.paid_at else None,
            'created_at': p.created_at.isoformat()
        })
    
    return JsonResponse({
        'status': 'ok',
        'data': {
            'mitra': {
                'id': str(mitra.id),
                'name': mitra.get_full_name() or mitra.username,
                'email': mitra.email,
                'phone_number': mitra.phone_number or '-',
                'is_verified': mitra.is_verified
            },
            'summary': {
                'total_earnings': total_earnings,
                'total_commission': total_commission,
                'total_transactions': len(transactions)
            },
            'transactions': transactions
        }
    })


# Refund Management APIs
@require_http_methods(["GET", "POST"])
@csrf_exempt
def api_refunds(request):
    """Combined endpoint: GET to list refunds, POST to create refund"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    if request.method == 'GET':
        # List all refunds
        refunds = Pendapatan.objects.filter(
            payment_status='refunded'
        ).select_related('mitra', 'booking', 'booking__user', 'booking__court', 'booking__court__venue').order_by('-updated_at')
        
        data = []
        for p in refunds:
            # Parse refund info from notes
            refund_reason = ''
            if p.notes and 'REFUND:' in p.notes:
                parts = p.notes.split('|')
                if len(parts) > 0:
                    refund_reason = parts[0].replace('REFUND:', '').strip()
            
            data.append({
                'id': str(p.id),
                'mitra_name': p.mitra.get_full_name() or p.mitra.username,
                'customer_name': p.booking.user.get_full_name() or p.booking.user.username,
                'venue_name': p.booking.court.venue.name,
                'court_name': p.booking.court.name,
                'amount': float(p.net_amount),
                'reason': refund_reason,
                'refunded_at': p.updated_at.isoformat(),
                'booking_date': p.booking.booking_date.isoformat()
            })
        
        return JsonResponse({'status': 'ok', 'data': data})
    
    elif request.method == 'POST':
        # Create refund
        try:
            data = json.loads(request.body)
            pendapatan_id = data.get('pendapatan_id')
            reason = data.get('reason', '')
            
            if not pendapatan_id:
                return JsonResponse({'status': 'error', 'message': 'pendapatan_id is required'}, status=400)
            
            pendapatan = Pendapatan.objects.get(id=pendapatan_id)
            
            # Check if already refunded
            if pendapatan.payment_status == 'refunded':
                return JsonResponse({'status': 'error', 'message': 'Already refunded'}, status=400)
            
            # Mark as refunded and add note
            pendapatan.payment_status = 'refunded'
            pendapatan.notes = f"REFUND: {reason} | Processed by: {request.user.username} | Original notes: {pendapatan.notes or ''}"
            pendapatan.save()
            
            return JsonResponse({
                'status': 'ok',
                'message': 'Refund processed successfully',
                'data': {
                    'pendapatan_id': str(pendapatan.id),
                    'amount': float(pendapatan.net_amount),
                    'status': 'refunded'
                }
            })
        except Pendapatan.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_create_refund(request, pendapatan_id):
    """Create a refund request by marking pendapatan as refunded"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        reason = data.get('reason', '')
        
        pendapatan = Pendapatan.objects.get(id=pendapatan_id)
        
        # Check if already refunded
        if pendapatan.payment_status == 'refunded':
            return JsonResponse({'status': 'error', 'message': 'Already refunded'}, status=400)
        
        # Mark as refunded and add note
        pendapatan.payment_status = 'refunded'
        pendapatan.notes = f"REFUND: {reason} | Processed by: {request.user.username} | Original notes: {pendapatan.notes or ''}"
        pendapatan.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Refund processed successfully',
            'data': {
                'pendapatan_id': str(pendapatan.id),
                'amount': float(pendapatan.net_amount),
                'status': 'refunded'
            }
        })
    except Pendapatan.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
@csrf_exempt
def api_list_refunds(request):
    """List all refunded transactions"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    refunds = Pendapatan.objects.filter(
        payment_status='refunded'
    ).select_related('mitra', 'booking', 'booking__user', 'booking__court', 'booking__court__venue').order_by('-updated_at')
    
    data = []
    for p in refunds:
        # Parse refund info from notes
        refund_reason = ''
        if p.notes and 'REFUND:' in p.notes:
            parts = p.notes.split('|')
            if len(parts) > 0:
                refund_reason = parts[0].replace('REFUND:', '').strip()
        
        data.append({
            'id': str(p.id),
            'mitra_name': p.mitra.get_full_name() or p.mitra.username,
            'customer_name': p.booking.user.get_full_name() or p.booking.user.username,
            'venue_name': p.booking.court.venue.name,
            'court_name': p.booking.court.name,
            'amount': float(p.net_amount),
            'reason': refund_reason,
            'refunded_at': p.updated_at.isoformat(),
            'booking_date': p.booking.booking_date.isoformat()
        })
    
    return JsonResponse({'status': 'ok', 'data': data})


@require_http_methods(["DELETE"])
@csrf_exempt
def api_cancel_refund(request, pendapatan_id):
    """Cancel a refund by reverting status back to paid"""
    if not request.user.is_authenticated or request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    try:
        pendapatan = Pendapatan.objects.get(id=pendapatan_id, payment_status='refunded')
        
        # Revert status
        pendapatan.payment_status = 'paid'
        # Keep the refund note for history but mark as cancelled
        pendapatan.notes = f"[CANCELLED] {pendapatan.notes}"
        pendapatan.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Refund cancelled successfully'
        })
    except Pendapatan.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Refunded transaction not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# Import forms and decorators from users app
from app.users.forms import CustomLoginForm, CustomUserCreationForm, CustomUserUpdateForm, VenueForm, CourtForm
from app.users.decorators import login_required, role_required, anonymous_required


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

# Public Venue Detail API (no authentication required)
@require_http_methods(["GET"])
def api_venue_detail(request, venue_id):
    try:
        print(f'Looking up venue with ID: {venue_id}')
        v = Venue.objects.get(pk=venue_id, verification_status='approved')
        print(f'Found venue: {v.name}')
        
        # Get venue images
        images = [img.image_url for img in v.images.all()]
        
        # Get venue facilities
        facilities = [
            {
                'name': vf.facility.name,
                'icon': vf.facility.icon.url if vf.facility.icon else None
            } for vf in VenueFacility.objects.filter(venue=v)
        ]
        
        # Get courts
        courts = [
            {
                'id': c.id,
                'name': c.name,
                'is_active': c.is_active,
                'price_per_hour': float(c.price_per_hour)
            } for c in v.courts.all()
        ]
        
        # Get ratings and reviews
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

        data = {
            'id': str(v.id),
            'name': v.name,
            'category': v.category.name if v.category else None,
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
        }
        return JsonResponse({'status': 'ok', 'data': data})
        
    except Venue.DoesNotExist:
        print(f'Venue not found: {venue_id}')
        return JsonResponse({'status': 'error', 'message': 'Venue not found'}, status=404)
    except Exception as e:
        print(f'Error retrieving venue: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
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
        # Get courts for this venue to calculate average price
        courts = venue.courts.all()
        total_price = sum(court.price_per_hour for court in courts)
        avg_price = total_price / len(courts) if courts else 0
        
        # Get primary image
        primary_image = venue.images.filter(is_primary=True).first()
        if not primary_image and venue.images.exists():
            primary_image = venue.images.first()
        
        venues_data.append({
            'id': str(venue.id),
            'name': venue.name,
            'address': venue.address,
            'number_of_courts': venue.number_of_courts,
            'verification_status': venue.verification_status,
            'is_verified': venue.is_verified,
            'avg_price_per_hour': float(avg_price),
            'total_courts': courts.count(),
            'image_url': primary_image.image_url if primary_image else None
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

@require_http_methods(["GET", "PUT", "DELETE"])
def api_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)

    user = request.user

    # Read
    if request.method == 'GET':
        user_data = {
            'id': str(user.id),
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'phone_number': user.phone_number,
            'address': user.address,
            'profile_picture': user.profile_picture,  # Return URL directly
            'created_at': user.created_at.isoformat() if getattr(user, 'created_at', None) else None,
        }
        return JsonResponse({'success': True, 'data': {'user': user_data}})

    # Update
    if request.method == 'PUT':
        try:
            # Always expect JSON since profile_picture is a URL field
            data = json.loads(request.body or '{}')
            password = data.pop('password', None)

            # Username uniqueness validation
            new_username = data.get('username', user.username)
            if new_username != user.username and User.objects.filter(username=new_username).exclude(id=user.id).exists():
                return JsonResponse({'success': False, 'message': 'Username sudah digunakan'}, status=400)

            form = CustomUserUpdateForm(data, instance=user)
            if form.is_valid():
                form.save()
                if password:
                    user.set_password(password)
                    user.save()

                ActivityLog.objects.create(
                    user=user,
                    action_type='update',
                    description=f'User {user.username} updated profile via API',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )

                updated = {
                    'id': str(user.id),
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'address': user.address,
                    'profile_picture': user.profile_picture,  # Return URL directly
                }
                return JsonResponse({'success': True, 'message': 'Profile updated', 'data': {'user': updated}})
            else:
                errors = {}
                for field, field_errors in form.errors.items():
                    errors[field] = [str(e) for e in field_errors]
                return JsonResponse({'success': False, 'message': 'Validation failed', 'errors': errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Server error: {str(e)}'}, status=500)
        
    # Delete
    if request.method == 'DELETE':
        try:
            ActivityLog.objects.create(
                user=user,
                action_type='delete',
                description=f'User {user.username} requested account deletion via API',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            username = user.username
            logout(request)
            user.delete()

            return JsonResponse({'success': True, 'message': f'Account {username} deleted'})
        except Exception:
            return JsonResponse({'success': False, 'message': 'Server error'}, status=500)

@require_http_methods(["DELETE"])
def api_booking_detail(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)

    booking = get_object_or_404(Booking, id=booking_id)

    if booking.user_id != request.user.id:
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)

    if booking.booking_date <= date.today():
        return JsonResponse({'success': False, 'message': 'Cannot cancel booking on or after booking day'}, status=400)

    try:
        booking.booking_status = 'cancelled'
        try:
            booking.payment_status = 'refunded'
        except Exception:
            pass
        booking.save()
        return JsonResponse({'success': True, 'message': 'Booking cancelled'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Failed to cancel booking'}, status=500)

# ============================================
# MITRA MANAGEMENT (Admin-facing) API
# ============================================


@csrf_exempt
@require_http_methods(["GET"])
def api_mitra_list(request):
    """Return list of mitra users as JSON. Uses existing User model (role='mitra')."""
    try:
        mitras = User.objects.filter(role='mitra')
        data = []
        for m in mitras:
            # derive status
            if m.is_verified:
                status = 'approved'
            else:
                status = 'pending' if m.is_active else 'rejected'

            # Get venue descriptions for this mitra
            venues = Venue.objects.filter(owner=m)
            venue_descriptions = []
            for venue in venues:
                if venue.description:
                    venue_descriptions.append(f"{venue.name}: {venue.description}")
            
            # Join all venue descriptions, or empty string if none
            deskripsi = ' | '.join(venue_descriptions) if venue_descriptions else ''

            # Get all courts from all venues owned by this mitra
            courts = []
            for venue in venues:
                venue_courts = Court.objects.filter(venue=venue)
                for court in venue_courts:
                    courts.append({
                        'id': str(court.id),
                        'name': court.name,
                        'description': court.description or 'Tidak ada deskripsi',
                        'venue_name': venue.name
                    })

            data.append({
                'id': str(m.id),
                'nama': m.get_full_name() or m.first_name or m.username,
                'email': m.email,
                'deskripsi': deskripsi,
                'gambar': m.profile_picture or '',
                'courts': courts,
                'tanggal_daftar': m.created_at.isoformat() if hasattr(m, 'created_at') else None,
                'status': status,
            })

        return JsonResponse({'status': 'ok', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
def api_mitra_update_status(request, mitra_id):
    """Patch endpoint to update mitra status. Body: {"status": "approved"|"rejected", "rejection_reason": "..."} """
    try:
        try:
            mitra = User.objects.get(id=mitra_id, role='mitra')
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mitra not found'}, status=404)

        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

        new_status = data.get('status')
        rejection_reason = data.get('rejection_reason', '')  # Accept rejection reason (not stored due to model constraints)
        
        if new_status not in ['approved', 'rejected']:
            return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)

        if new_status == 'approved':
            mitra.is_verified = True
            mitra.is_active = True
        else:  # rejected
            mitra.is_verified = False
            # mark as inactive to reflect rejection without changing models
            mitra.is_active = False
            # Note: rejection_reason is received but not stored (no field in model)

        mitra.save()

        return JsonResponse({
            'status': 'ok',
            'message': f'Mitra {new_status} successfully',
            'data': {
                'id': str(mitra.id),
                'status': new_status
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_mitra_venue_details(request, mitra_id):
    """Get detailed venue information for a specific mitra"""
    try:
        try:
            mitra = User.objects.get(id=mitra_id, role='mitra')
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mitra not found'}, status=404)

        # Get all venues for this mitra
        venues = Venue.objects.filter(owner=mitra).prefetch_related('images', 'courts', 'courts__images')
        
        venues_data = []
        for venue in venues:
            # Get venue images
            venue_images = []
            for img in venue.images.all():
                venue_images.append({
                    'id': img.id,
                    'url': img.image_url,
                    'is_primary': img.is_primary,
                    'caption': img.caption or ''
                })
            
            # Get courts for this venue
            courts_data = []
            for court in venue.courts.all():
                court_images = []
                for img in court.images.all():
                    court_images.append({
                        'id': img.id,
                        'url': img.image_url,
                        'is_primary': img.is_primary,
                        'caption': img.caption or ''
                    })
                
                courts_data.append({
                    'id': court.id,
                    'name': court.name,
                    'category': court.category.get_name_display() if court.category else 'N/A',
                    'price_per_hour': str(court.price_per_hour),
                    'is_active': court.is_active,
                    'description': court.description or 'Tidak ada deskripsi',
                    'images': court_images
                })
            
            venues_data.append({
                'id': str(venue.id),
                'name': venue.name,
                'address': venue.address,
                'contact': venue.contact or '-',
                'description': venue.description or 'Tidak ada deskripsi',
                'number_of_courts': venue.number_of_courts,
                'verification_status': venue.verification_status,
                'is_verified': venue.is_verified,
                'created_at': venue.created_at.isoformat() if hasattr(venue, 'created_at') else None,
                'images': venue_images,
                'courts': courts_data
            })

        return JsonResponse({
            'status': 'ok',
            'data': {
                'mitra': {
                    'id': str(mitra.id),
                    'name': mitra.get_full_name() or mitra.first_name or mitra.username,
                    'email': mitra.email,
                    'profile_picture': mitra.profile_picture or '',
                    'phone_number': mitra.phone_number or '-'
                },
                'venues': venues_data
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ============================================
# MITRA API ENDPOINTS
# ============================================

@require_http_methods(["GET", "POST"])
def api_venues(request):
    """API endpoint for listing and creating venues"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'mitra':
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Mitra role required.'
        }, status=403)
    
    if request.method == 'GET':
        # List all venues for the mitra
        venues = Venue.objects.filter(owner=request.user)
        venues_data = []
        
        for venue in venues:
            # Get venue images
            images = []
            for img in venue.images.all():
                images.append({
                    'id': img.id,
                    'url': img.image_url,
                    'is_primary': img.is_primary,
                    'caption': img.caption
                })
            
            venues_data.append({
                'id': str(venue.id),
                'name': venue.name,
                'address': venue.address,
                'location_url': venue.location_url,
                'contact': venue.contact,
                'description': venue.description,
                'number_of_courts': venue.number_of_courts,
                'verification_status': venue.verification_status,
                'is_verified': venue.is_verified,
                'created_at': venue.created_at.isoformat(),
                'updated_at': venue.updated_at.isoformat(),
                'images': images
            })
        
        return JsonResponse({
            'success': True,
            'data': venues_data
        })
    
    elif request.method == 'POST':
        # Create a new venue
        try:
            # Handle form data
            form = VenueForm(request.POST)
            
            if form.is_valid():
                venue = form.save(commit=False)
                venue.owner = request.user
                venue.save()
                
                # Handle image URLs (JSON array of URLs)
                image_urls_str = request.POST.get('image_urls', '[]')
                try:
                    image_urls = json.loads(image_urls_str)
                    from app.venues.models import VenueImage
                    for idx, url in enumerate(image_urls):
                        if url and url.strip():
                            VenueImage.objects.create(
                                venue=venue,
                                image_url=url.strip(),
                                is_primary=(idx == 0)  # First image is primary
                            )
                except (json.JSONDecodeError, ValueError):
                    pass  # Continue without images if parsing fails
                
                # Log the activity
                ActivityLog.objects.create(
                    user=request.user,
                    action_type='create',
                    description=f'Created new venue: {venue.name}',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Venue berhasil ditambahkan!',
                    'data': {
                        'id': str(venue.id),
                        'name': venue.name,
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Data tidak valid',
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)


@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def api_venue_detail(request, venue_id):
    """API endpoint for getting, updating, and deleting a specific venue"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'mitra':
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Mitra role required.'
        }, status=403)
    
    try:
        venue = Venue.objects.get(id=venue_id, owner=request.user)
    except Venue.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Venue tidak ditemukan'
        }, status=404)
    
    if request.method == 'GET':
        # Get venue details
        # Get venue images
        images = []
        for img in venue.images.all():
            images.append({
                'id': img.id,
                'url': img.image_url,
                'is_primary': img.is_primary,
                'caption': img.caption
            })
        
        venue_data = {
            'id': str(venue.id),
            'name': venue.name,
            'address': venue.address,
            'location_url': venue.location_url,
            'contact': venue.contact,
            'description': venue.description,
            'number_of_courts': venue.number_of_courts,
            'verification_status': venue.verification_status,
            'is_verified': venue.is_verified,
            'created_at': venue.created_at.isoformat(),
            'updated_at': venue.updated_at.isoformat(),
            'images': images
        }
        
        return JsonResponse({
            'success': True,
            'data': venue_data
        })
    
    elif request.method in ['POST', 'PUT']:
        # Update venue
        try:
            form = VenueForm(request.POST, instance=venue)
            
            if form.is_valid():
                venue = form.save()
                
                # Handle image URLs update
                # Delete images not in the submitted list, add new ones
                image_urls_str = request.POST.get('image_urls', '')
                if image_urls_str:
                    try:
                        image_urls = json.loads(image_urls_str)
                        from app.venues.models import VenueImage
                        
                        # Clean and normalize submitted URLs
                        submitted_urls = [url.strip() for url in image_urls if url and url.strip()]
                        
                        # Delete images that are not in the submitted list
                        venue.images.exclude(image_url__in=submitted_urls).delete()
                        
                        # Get current image URLs after deletion
                        existing_urls = set(venue.images.values_list('image_url', flat=True))
                        
                        # Add new images that don't exist yet
                        for idx, url in enumerate(submitted_urls):
                            if url not in existing_urls:
                                is_primary = (idx == 0 and not venue.images.filter(is_primary=True).exists())
                                VenueImage.objects.create(
                                    venue=venue,
                                    image_url=url,
                                    is_primary=is_primary
                                )
                    except (json.JSONDecodeError, ValueError):
                        pass  # Continue without images if parsing fails
                
                # Log the activity
                ActivityLog.objects.create(
                    user=request.user,
                    action_type='update',
                    description=f'Updated venue: {venue.name}',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Venue berhasil diupdate!',
                    'data': {
                        'id': str(venue.id),
                        'name': venue.name,
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Data tidak valid',
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)
    
    elif request.method == 'DELETE':
        # Delete venue
        try:
            venue_name = venue.name
            venue.delete()
            
            # Log the activity
            ActivityLog.objects.create(
                user=request.user,
                action_type='delete',
                description=f'Deleted venue: {venue_name}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Venue berhasil dihapus!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)


@require_http_methods(["GET", "POST"])
def api_courts(request):
    """API endpoint for listing and creating courts"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'mitra':
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Mitra role required.'
        }, status=403)
    
    if request.method == 'GET':
        # List all courts for the mitra's venues
        venue_id = request.GET.get('venue_id')
        
        if venue_id:
            courts = Court.objects.filter(venue__owner=request.user, venue__id=venue_id).select_related('venue', 'category')
        else:
            courts = Court.objects.filter(venue__owner=request.user).select_related('venue', 'category')
        
        courts_data = []
        for court in courts:
            # Get court images
            images = []
            for img in court.images.all():
                images.append({
                    'id': img.id,
                    'url': img.image_url,
                    'is_primary': img.is_primary,
                    'caption': img.caption
                })
            
            courts_data.append({
                'id': court.id,
                'name': court.name,
                'venue_id': str(court.venue.id),
                'venue_name': court.venue.name,
                'category': court.category.get_name_display() if court.category else None,
                'category_id': court.category.id if court.category else None,
                'price_per_hour': str(court.price_per_hour),
                'is_active': court.is_active,
                'maintenance_notes': court.maintenance_notes,
                'description': court.description,
                'images': images
            })
        
        return JsonResponse({
            'success': True,
            'data': courts_data
        })
    
    elif request.method == 'POST':
        # Create a new court
        try:
            form = CourtForm(request.POST, user=request.user)
            
            if form.is_valid():
                court = form.save()
                
                # Handle image URLs (JSON array of URLs)
                image_urls_str = request.POST.get('image_urls', '[]')
                try:
                    image_urls = json.loads(image_urls_str)
                    from app.courts.models import CourtImage
                    for idx, url in enumerate(image_urls):
                        if url and url.strip():
                            CourtImage.objects.create(
                                court=court,
                                image_url=url.strip(),
                                is_primary=(idx == 0)  # First image is primary
                            )
                except (json.JSONDecodeError, ValueError):
                    pass  # Continue without images if parsing fails
                
                # Handle session slots
                sessions_json = request.POST.get('sessions', '[]')
                try:
                    sessions = json.loads(sessions_json)
                    from app.courts.models import CourtSession
                    for session_data in sessions:
                        CourtSession.objects.create(
                            court=court,
                            session_name=session_data.get('session_name', ''),
                            start_time=session_data.get('start_time'),
                            end_time=session_data.get('end_time'),
                            is_active=session_data.get('is_active', True)
                        )
                except (json.JSONDecodeError, ValueError) as e:
                    # If session parsing fails, continue without sessions
                    pass
                
                # Log the activity
                ActivityLog.objects.create(
                    user=request.user,
                    action_type='create',
                    description=f'Created new court: {court.name} at {court.venue.name}',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Lapangan berhasil ditambahkan!',
                    'data': {
                        'id': court.id,
                        'name': court.name,
                        'venue_name': court.venue.name,
                        'category': court.category.get_name_display() if court.category else None,
                        'price_per_hour': str(court.price_per_hour),
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Data tidak valid',
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)


@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def api_court_detail(request, court_id):
    """API endpoint for getting, updating, and deleting a specific court"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'mitra':
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Mitra role required.'
        }, status=403)
    
    try:
        court = Court.objects.get(id=court_id, venue__owner=request.user)
    except Court.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Lapangan tidak ditemukan'
        }, status=404)
    
    if request.method == 'GET':
        # Get court details
        # Get court images
        images = []
        for img in court.images.all():
            images.append({
                'id': img.id,
                'url': img.image_url,
                'is_primary': img.is_primary,
                'caption': img.caption
            })
        
        # Get court sessions
        from app.courts.models import CourtSession
        sessions = []
        for session in court.sessions.all():
            # Count total bookings for this session (pending or confirmed)
            total_bookings = Booking.objects.filter(
                court=court,
                session=session,
                booking_status__in=['pending', 'confirmed']
            ).count()
            
            sessions.append({
                'id': session.id,
                'session_name': session.session_name,
                'start_time': session.start_time.strftime('%H:%M'),
                'end_time': session.end_time.strftime('%H:%M'),
                'is_active': session.is_active,
                'total_bookings': total_bookings
            })
        
        court_data = {
            'id': court.id,
            'name': court.name,
            'venue_id': str(court.venue.id),
            'venue_name': court.venue.name,
            'venue_address': court.venue.address,
            'category': court.category.get_name_display() if court.category else None,
            'category_id': court.category.id if court.category else None,
            'price_per_hour': str(court.price_per_hour),
            'is_active': court.is_active,
            'maintenance_notes': court.maintenance_notes,
            'description': court.description,
            'images': images,
            'sessions': sessions
        }
        
        return JsonResponse({
            'success': True,
            'data': court_data
        })
    
    elif request.method in ['POST', 'PUT']:
        # Update court
        try:
            form = CourtForm(request.POST, instance=court, user=request.user)
            
            if form.is_valid():
                court = form.save()
                
                # Handle image URLs update
                # Delete images not in the submitted list, add new ones
                image_urls_str = request.POST.get('image_urls', '')
                if image_urls_str:
                    try:
                        image_urls = json.loads(image_urls_str)
                        from app.courts.models import CourtImage
                        
                        # Clean and normalize submitted URLs
                        submitted_urls = [url.strip() for url in image_urls if url and url.strip()]
                        
                        # Delete images that are not in the submitted list
                        court.images.exclude(image_url__in=submitted_urls).delete()
                        
                        # Get current image URLs after deletion
                        existing_urls = set(court.images.values_list('image_url', flat=True))
                        
                        # Add new images that don't exist yet
                        for idx, url in enumerate(submitted_urls):
                            if url not in existing_urls:
                                is_primary = (idx == 0 and not court.images.filter(is_primary=True).exists())
                                CourtImage.objects.create(
                                    court=court,
                                    image_url=url,
                                    is_primary=is_primary
                                )
                    except (json.JSONDecodeError, ValueError):
                        pass  # Continue without images if parsing fails
                
                # Handle session slots update
                sessions_json = request.POST.get('sessions', '[]')
                try:
                    sessions = json.loads(sessions_json)
                    from app.courts.models import CourtSession
                    
                    # Get existing session IDs from the form data
                    existing_session_ids = [s.get('id') for s in sessions if s.get('id')]
                    
                    # Delete sessions that are not in the updated list
                    court.sessions.exclude(id__in=existing_session_ids).delete()
                    
                    # Create or update sessions
                    for session_data in sessions:
                        session_id = session_data.get('id')
                        if session_id:
                            # Update existing session
                            try:
                                session = CourtSession.objects.get(id=session_id, court=court)
                                session.session_name = session_data.get('session_name', '')
                                session.start_time = session_data.get('start_time')
                                session.end_time = session_data.get('end_time')
                                session.is_active = session_data.get('is_active', True)
                                session.save()
                            except CourtSession.DoesNotExist:
                                pass
                        else:
                            # Create new session
                            CourtSession.objects.create(
                                court=court,
                                session_name=session_data.get('session_name', ''),
                                start_time=session_data.get('start_time'),
                                end_time=session_data.get('end_time'),
                                is_active=session_data.get('is_active', True)
                            )
                except (json.JSONDecodeError, ValueError) as e:
                    # If session parsing fails, continue without updating sessions
                    pass
                
                # Log the activity
                ActivityLog.objects.create(
                    user=request.user,
                    action_type='update',
                    description=f'Updated court: {court.name} at {court.venue.name}',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Lapangan berhasil diupdate!',
                    'data': {
                        'id': court.id,
                        'name': court.name,
                        'venue_name': court.venue.name,
                        'category': court.category.get_name_display() if court.category else None,
                        'price_per_hour': str(court.price_per_hour),
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Data tidak valid',
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)
    
    elif request.method == 'DELETE':
        # Delete court
        try:
            court_name = court.name
            venue_name = court.venue.name
            court.delete()
            
            # Log the activity
            ActivityLog.objects.create(
                user=request.user,
                action_type='delete',
                description=f'Deleted court: {court_name} at {venue_name}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Lapangan berhasil dihapus!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)


# Review Management APIs
@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_venue_reviews(request, venue_id):
    """API endpoint for listing and creating venue reviews"""
    try:
        venue = Venue.objects.get(pk=venue_id)
    except Venue.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Venue not found'}, status=404)

    if request.method == "GET":
        # Get all reviews for this venue
        reviews = Review.objects.filter(
            booking__court__venue=venue
        ).select_related('booking__user').order_by('-created_at')

        reviews_data = [{
            'id': str(review.id),
            'user': review.booking.user.username,
            'user_full_name': review.booking.user.get_full_name(),
            'rating': float(review.rating),
            'comment': review.comment,
            'created_at': review.created_at.isoformat()
        } for review in reviews]

        # Calculate average rating
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        return JsonResponse({
            'status': 'success',
            'data': {
                'reviews': reviews_data,
                'avg_rating': float(avg_rating),
                'total_reviews': len(reviews_data)
            }
        })

    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)

        try:
            data = json.loads(request.body)
            rating = data.get('rating')
            comment = data.get('comment', '')

            if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Rating harus antara 1 dan 5'
                }, status=400)

            # Find the most recent completed booking for this user at this venue
            booking = Booking.objects.filter(
                court__venue=venue,
                user=request.user,
                booking_status='completed'
            ).exclude(
                review__isnull=False  # Exclude bookings that already have reviews
            ).order_by('-booking_date').first()

            if not booking:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Anda harus menyelesaikan booking terlebih dahulu untuk memberikan review'
                }, status=400)

            # Create the review
            review = Review.objects.create(
                booking=booking,
                rating=rating,
                comment=comment
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Review berhasil ditambahkan',
                'data': {
                    'id': str(review.id),
                    'rating': float(review.rating),
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def api_manage_review(request, review_id):
    """API endpoint for updating and deleting reviews"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)

    try:
        review = Review.objects.get(pk=review_id)
        
        # Check if user owns this review
        if review.booking and review.booking.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

        if request.method == "PUT":
            data = json.loads(request.body)
            rating = data.get('rating')
            comment = data.get('comment', review.comment)

            if rating is not None:
                if not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Rating harus antara 0 dan 5'
                    }, status=400)
                review.rating = rating

            review.comment = comment
            review.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Review berhasil diupdate',
                'data': {
                    'id': str(review.id),
                    'rating': float(review.rating),
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                }
            })

        elif request.method == "DELETE":
            review.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Review berhasil dihapus'
            })

    except Review.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Review not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def api_court_sessions(request, court_id):
    """API endpoint for getting available sessions for a specific court with booking status"""
    try:
        court = Court.objects.get(id=court_id)
        
        # Get date parameter (optional, for checking booking status on specific date)
        booking_date = request.GET.get('date')  # Format: YYYY-MM-DD
        
        # Get all active sessions for this court
        sessions = CourtSession.objects.filter(
            court=court,
            is_active=True
        ).order_by('start_time')
        
        sessions_data = []
        for session in sessions:
            session_info = {
                'id': session.id,
                'session_name': session.session_name,
                'start_time': session.start_time.strftime('%H:%M'),
                'end_time': session.end_time.strftime('%H:%M'),
                'is_active': session.is_active,
                'is_booked': False,
                'booking_id': None
            }
            
            # Check if this session is booked on the specified date
            if booking_date:
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
                    
                    # Check for confirmed or pending bookings for this session on this date
                    booking = Booking.objects.filter(
                        court=court,
                        session=session,
                        booking_date=date_obj,
                        booking_status__in=['pending', 'confirmed']
                    ).first()
                    
                    if booking:
                        session_info['is_booked'] = True
                        session_info['booking_id'] = str(booking.id)
                except ValueError:
                    pass  # Invalid date format, continue without booking check
            
            sessions_data.append(session_info)
        
        return JsonResponse({
            'success': True,
            'court_id': court.id,
            'court_name': court.name,
            'sessions': sessions_data,
            'date': booking_date
        })
        
    except Court.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Lapangan tidak ditemukan'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def api_pendapatan(request):
    """API endpoint for getting mitra's revenue/earnings data"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'mitra':
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Mitra role required.'
        }, status=403)
    
    # Get filter parameters
    period = request.GET.get('period', 'all')  # all, month, year
    
    # Base queryset
    pendapatan_qs = Pendapatan.objects.filter(mitra=request.user)
    
    # Apply filters
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    if period == 'month':
        start_date = timezone.now() - timedelta(days=30)
        pendapatan_qs = pendapatan_qs.filter(created_at__gte=start_date)
    elif period == 'year':
        start_date = timezone.now() - timedelta(days=365)
        pendapatan_qs = pendapatan_qs.filter(created_at__gte=start_date)
    
    # Calculate statistics
    total_pendapatan = pendapatan_qs.aggregate(
        total=Sum('net_amount')
    )['total'] or Decimal('0.00')
    
    total_commission = pendapatan_qs.aggregate(
        total=Sum('commission_amount')
    )['total'] or Decimal('0.00')
    
    total_bookings = pendapatan_qs.count()
    
    paid_amount = pendapatan_qs.filter(payment_status='paid').aggregate(
        total=Sum('net_amount')
    )['total'] or Decimal('0.00')
    
    pending_amount = pendapatan_qs.filter(payment_status='pending').aggregate(
        total=Sum('net_amount')
    )['total'] or Decimal('0.00')
    
    # Get detailed pendapatan records
    pendapatan_list = []
    for p in pendapatan_qs.select_related('booking', 'booking__court', 'booking__court__venue')[:50]:
        pendapatan_list.append({
            'id': str(p.id),
            'venue_name': p.booking.court.venue.name,
            'court_name': p.booking.court.name,
            'booking_date': p.booking.booking_date.isoformat(),
            'amount': str(p.amount),
            'commission_amount': str(p.commission_amount),
            'commission_rate': str(p.commission_rate),
            'net_amount': str(p.net_amount),
            'payment_status': p.payment_status,
            'paid_at': p.paid_at.isoformat() if p.paid_at else None,
            'created_at': p.created_at.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'statistics': {
                'total_pendapatan': str(total_pendapatan),
                'total_commission': str(total_commission),
                'total_bookings': total_bookings,
                'paid_amount': str(paid_amount),
                'pending_amount': str(pending_amount),
            },
            'pendapatan_list': pendapatan_list,
            'period': period
        }
    })


@require_http_methods(["GET"])
def api_sports_categories(request):
    """API endpoint for getting all sports categories"""
    categories = SportsCategory.objects.all()
    categories_data = []
    
    for category in categories:
        categories_data.append({
            'id': category.id,
            'name': category.name,
            'display_name': category.get_name_display(),
            'description': category.description,
        })
    
    return JsonResponse({
        'success': True,
        'data': categories_data
    })


@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_venue_image(request, image_id):
    """API endpoint for deleting a venue image"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'mitra':
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Mitra role required.'
        }, status=403)
    
    try:
        from app.venues.models import VenueImage
        image = VenueImage.objects.get(id=image_id, venue__owner=request.user)
        image.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Gambar berhasil dihapus!'
        })
    except VenueImage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Gambar tidak ditemukan'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_court_image(request, image_id):
    """API endpoint for deleting a court image"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'mitra':
        return JsonResponse({
            'success': False,
            'message': 'Access denied. Mitra role required.'
        }, status=403)
    
    try:
        from app.courts.models import CourtImage
        image = CourtImage.objects.get(id=image_id, court__venue__owner=request.user)
        image.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Gambar berhasil dihapus!'
        })
    except CourtImage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Gambar tidak ditemukan'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }, status=500)


# Booking Management APIs for Mitra
@login_required
@role_required('mitra')
def api_bookings(request):
    """Get all bookings for mitra's venues"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    
    try:
        # Get filter parameters
        status_filter = request.GET.get('status', 'all')
        venue_filter = request.GET.get('venue_id', '')
        court_filter = request.GET.get('court_id', '')
        court_param = request.GET.get('court', '')  # Alternative court parameter
        date_filter = request.GET.get('date', '')
        session_filter = request.GET.get('session', '')
        
        # Get all bookings for mitra's courts
        bookings_qs = Booking.objects.filter(
            court__venue__owner=request.user
        ).select_related('user', 'court', 'court__venue', 'payment', 'session').order_by('-created_at')
        
        # Apply filters
        if status_filter != 'all':
            bookings_qs = bookings_qs.filter(booking_status=status_filter)
        
        if venue_filter:
            bookings_qs = bookings_qs.filter(court__venue_id=venue_filter)
        
        if court_filter:
            bookings_qs = bookings_qs.filter(court_id=court_filter)
        
        if court_param:
            bookings_qs = bookings_qs.filter(court_id=court_param)
        
        if session_filter:
            bookings_qs = bookings_qs.filter(session_id=session_filter)
        
        if date_filter:
            from datetime import datetime
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            bookings_qs = bookings_qs.filter(booking_date=date_obj)
        
        # Get statistics
        total_bookings = bookings_qs.count()
        pending_count = bookings_qs.filter(booking_status='pending').count()
        confirmed_count = bookings_qs.filter(booking_status='confirmed').count()
        completed_count = bookings_qs.filter(booking_status='completed').count()
        cancelled_count = bookings_qs.filter(booking_status='cancelled').count()
        
        # Prepare booking list
        bookings_list = []
        for booking in bookings_qs[:100]:  # Limit to 100 most recent
            # Get payment info
            payment_info = None
            try:
                if hasattr(booking, 'payment'):
                    payment_info = {
                        'method': booking.payment.payment_method,
                        'transaction_id': booking.payment.transaction_id,
                        'paid_at': booking.payment.paid_at.isoformat() if booking.payment.paid_at else None,
                        'has_proof': bool(booking.payment.payment_proof),
                        'proof_url': booking.payment.payment_proof if booking.payment.payment_proof else None
                    }
            except:
                pass
            
            bookings_list.append({
                'id': str(booking.id),
                'user_name': booking.user.get_full_name() or booking.user.username,
                'user_email': booking.user.email,
                'user_phone': booking.user.phone_number,
                'customer_name': booking.user.get_full_name() or booking.user.username,
                'customer_email': booking.user.email,
                'customer_phone': booking.user.phone_number,
                'venue_name': booking.court.venue.name,
                'venue_id': booking.court.venue.id,
                'court_name': booking.court.name,
                'court_id': booking.court.id,
                'session_name': booking.session.session_name if booking.session else None,
                'session_id': booking.session.id if booking.session else None,
                'booking_date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'duration_hours': str(booking.duration_hours),
                'total_price': str(booking.total_price),
                'booking_status': booking.booking_status,
                'payment_status': booking.payment_status,
                'notes': booking.notes,
                'cancellation_reason': booking.cancellation_reason,
                'created_at': booking.created_at.isoformat(),
                'payment': payment_info
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'bookings': bookings_list,
                'statistics': {
                    'total': total_bookings,
                    'pending': pending_count,
                    'confirmed': confirmed_count,
                    'completed': completed_count,
                    'cancelled': cancelled_count
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }, status=500)


@login_required
@role_required('mitra')
def api_booking_detail(request, booking_id):
    """Get or update a specific booking"""
    try:
        booking = Booking.objects.select_related(
            'user', 'court', 'court__venue', 'payment'
        ).get(id=booking_id, court__venue__owner=request.user)
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking tidak ditemukan'
        }, status=404)
    
    if request.method == 'GET':
        # Get payment info
        payment_info = None
        try:
            if hasattr(booking, 'payment'):
                payment_info = {
                    'method': booking.payment.payment_method,
                    'transaction_id': booking.payment.transaction_id,
                    'paid_at': booking.payment.paid_at.isoformat() if booking.payment.paid_at else None,
                    'has_proof': bool(booking.payment.payment_proof),
                    'proof_url': booking.payment.payment_proof if booking.payment.payment_proof else None,
                    'notes': booking.payment.notes
                }
        except:
            pass
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': str(booking.id),
                'customer_name': booking.user.get_full_name() or booking.user.username,
                'customer_email': booking.user.email,
                'customer_phone': booking.user.phone_number,
                'venue_name': booking.court.venue.name,
                'venue_id': booking.court.venue.id,
                'court_name': booking.court.name,
                'court_id': booking.court.id,
                'booking_date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'duration_hours': str(booking.duration_hours),
                'total_price': str(booking.total_price),
                'booking_status': booking.booking_status,
                'payment_status': booking.payment_status,
                'notes': booking.notes,
                'cancellation_reason': booking.cancellation_reason,
                'created_at': booking.created_at.isoformat(),
                'updated_at': booking.updated_at.isoformat(),
                'payment': payment_info
            }
        })
    
    elif request.method == 'POST':
        # Update booking status
        try:
            # Try to get data from JSON first, then fall back to FormData
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            new_status = data.get('booking_status')
            cancellation_reason = data.get('cancellation_reason', '')
            
            if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
                return JsonResponse({
                    'success': False,
                    'message': 'Status booking tidak valid'
                }, status=400)
            
            booking.booking_status = new_status
            if new_status == 'cancelled' and cancellation_reason:
                booking.cancellation_reason = cancellation_reason
            
            booking.save()
            
            # Log the activity
            ActivityLog.objects.create(
                user=request.user,
                action_type='update',
                description=f'Updated booking {booking.id} status to {new_status}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Status booking berhasil diubah menjadi {new_status}',
                'data': {
                    'id': str(booking.id),
                    'booking_status': booking.booking_status
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Data tidak valid'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)
