from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Avg
from decimal import Decimal
import json
from datetime import date, datetime, timedelta
from django.utils import timezone

from app.users.models import User
from app.venues.models import Venue, VenueFacility, OperationalHour
from app.courts.models import Court
from app.bookings.models import Booking
from app.reviews.models import Review
from app.revenue.models import Pendapatan, ActivityLog

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
def api_mitra_dashboard(request):
    """API endpoint for mitra dashboard data with complete venue and court information"""
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
    
    today = date.today()
    
    for venue in venues:
        # Get all courts for this venue
        courts = venue.courts.all()
        total_price = sum(court.price_per_hour for court in courts)
        avg_price = total_price / len(courts) if courts else 0
        
        # Get unique sport categories from courts
        categories = set()
        for court in courts:
            if court.category:
                categories.add(court.category.get_name_display())
        categories_list = sorted(list(categories))
        
        # Get ALL venue images (not just primary)
        all_images = []
        for img in venue.images.all().order_by('-is_primary', 'id'):
            all_images.append({
                'id': str(img.id),
                'image_url': img.image_url,
                'is_primary': img.is_primary
            })
        
        # Get primary image
        primary_image = venue.images.filter(is_primary=True).first()
        if not primary_image and venue.images.exists():
            primary_image = venue.images.first()
        
        # Get facilities with full details
        facilities = []
        for vf in VenueFacility.objects.filter(venue=venue).select_related('facility'):
            facilities.append({
                'id': str(vf.facility.id),
                'name': vf.facility.name,
                'icon': vf.facility.icon
            })
        
        # Get operational hours
        operational_hours = []
        for oh in OperationalHour.objects.filter(venue=venue).order_by('day_of_week'):
            operational_hours.append({
                'id': str(oh.id),
                'day_of_week': oh.day_of_week,
                'day_name': oh.get_day_of_week_display(),
                'open_time': oh.open_time.strftime('%H:%M') if oh.open_time else None,
                'close_time': oh.close_time.strftime('%H:%M') if oh.close_time else None,
                'is_open': oh.is_open
            })
        
        # Get reviews and calculate average rating
        reviews = Review.objects.filter(booking__court__venue=venue).select_related('booking__user')
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
        rating_count = reviews.count()
        
        reviews_data = []
        for review in reviews.order_by('-created_at')[:10]:  # Latest 10 reviews
            reviews_data.append({
                'id': str(review.id),
                'rating': review.rating,
                'review_text': review.review_text,
                'created_at': review.created_at.isoformat() if review.created_at else None,
                'user': {
                    'username': review.booking.user.username,
                    'first_name': review.booking.user.first_name,
                    'last_name': review.booking.user.last_name
                }
            })
        
        # Get detailed court information with sessions and availability
        courts_data = []
        for court in courts:
            # Get all sessions for this court
            sessions = court.sessions.all()
            sessions_data = []
            
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
                
                sessions_data.append({
                    'id': str(session.id),
                    'session_name': session.session_name,
                    'start_time': session.start_time.strftime('%H:%M'),
                    'end_time': session.end_time.strftime('%H:%M'),
                    'duration': duration_minutes,
                    'is_available': not is_booked
                })
            
            courts_data.append({
                'id': str(court.id),
                'name': court.name,
                'price_per_hour': float(court.price_per_hour),
                'category': {
                    'code': court.category.name if court.category else None,
                    'display_name': court.category.get_name_display() if court.category else None
                } if court.category else None,
                'sessions': sessions_data,
                'total_sessions': len(sessions_data),
                'available_sessions': sum(1 for s in sessions_data if s['is_available'])
            })
        
        venues_data.append({
            'id': str(venue.id),
            'name': venue.name,
            'description': venue.description or '',
            'address': venue.address,
            'contact': venue.contact or '',
            'location_url': venue.location_url or '',
            'number_of_courts': venue.number_of_courts,
            'verification_status': venue.verification_status,
            'is_verified': venue.is_verified,
            'avg_price_per_hour': float(avg_price),
            'total_courts': courts.count(),
            
            # Images
            'image_url': primary_image.image_url if primary_image else None,
            'images': all_images,
            
            # Categories and facilities
            'sport_categories': categories_list,
            'facilities': facilities,
            
            # Operational hours
            'operational_hours': operational_hours,
            
            # Reviews and ratings
            'avg_rating': round(avg_rating, 1),
            'rating_count': rating_count,
            'reviews': reviews_data,
            
            # Detailed courts with sessions
            'courts': courts_data
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

@require_http_methods(["GET"])
@csrf_exempt
def api_mitra_earnings(request):
    """Return each mitra's total earnings based on completed transactions (paid, excluding refunded)."""
    if not request.user.is_authenticated or request.user.role != 'admin':
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)

    mitras = User.objects.filter(role='mitra')
    data = []
    for mitra in mitras:
        # Sum net_amount for Pendapatan where payment_status is 'paid' (NOT refunded)
        # Only count transactions where booking is completed
        total_earnings = Pendapatan.objects.filter(
            mitra=mitra,
            payment_status='paid',
            booking__booking_status='completed'
        ).aggregate(total=Sum('net_amount'))['total'] or 0
        
        # Count completed and paid transactions (excluding refunded)
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
            'completed_transactions': completed_transactions,
        })
    return JsonResponse({'status': 'ok', 'data': data})

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
            # Also approve all venues owned by this mitra
            Venue.objects.filter(owner=mitra).update(verification_status='approved')
        else:  # rejected
            mitra.is_verified = False
            # mark as inactive to reflect rejection without changing models
            mitra.is_active = False
            # Also reject all venues owned by this mitra
            Venue.objects.filter(owner=mitra).update(verification_status='rejected')
            # Note: rejection_reason is received but not stored (no field in model)

        mitra.save()

        # Get count of venues affected
        venues_count = Venue.objects.filter(owner=mitra).count()

        return JsonResponse({
            'status': 'ok',
            'message': f'Mitra {new_status} successfully. {venues_count} venue(s) also {new_status}.',
            'data': {
                'id': str(mitra.id),
                'status': new_status,
                'venues_affected': venues_count
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
    
    # Get all completed and paid transactions for this mitra (EXCLUDING refunded)
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
            'pendapatan_id': str(p.id),  # Added pendapatan_id for refund processing
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
            'payment_status': p.payment_status,
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
                'total_transactions': len(transactions),
            },
            'transactions': transactions,
        }
    })
