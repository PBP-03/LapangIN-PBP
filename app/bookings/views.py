from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from decimal import Decimal
import json
import traceback
from datetime import date, datetime

# Import models
from app.courts.models import Court, CourtSession
from app.bookings.models import Booking, Payment
from app.revenue.models import Pendapatan, ActivityLog

# Import decorators
from app.users.decorators import login_required, role_required


def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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


# Create Booking Endpoint
@csrf_exempt
@require_http_methods(["POST"])
def create_booking(request):
    """Create a new booking with payment"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
    
    # Only users can create bookings, not mitra or admin
    if request.user.role != 'user':
        return JsonResponse({
            'success': False,
            'message': 'Only regular users can create bookings. Mitra and admin accounts cannot book venues.'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        court_id = data.get('court_id')
        session_ids = data.get('session_ids', [])
        booking_date = data.get('booking_date')
        payment_method = data.get('payment_method')
        notes = data.get('notes', '')
        auto_confirm = data.get('auto_confirm', False)  # For testing
        
        # Validate required fields
        if not court_id or not session_ids or not booking_date or not payment_method:
            return JsonResponse({
                'success': False,
                'message': 'Missing required fields'
            }, status=400)
        
        # Get court
        try:
            court = Court.objects.get(pk=court_id)
        except Court.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Court not found'
            }, status=404)
        
        # Get sessions
        sessions = CourtSession.objects.filter(id__in=session_ids, court=court)
        if sessions.count() != len(session_ids):
            return JsonResponse({
                'success': False,
                'message': 'One or more sessions not found'
            }, status=404)
        
        # Parse booking date
        try:
            booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid date format'
            }, status=400)
        
        # Check if booking date is in the past
        if booking_date_obj < date.today():
            return JsonResponse({
                'success': False,
                'message': 'Cannot book for past dates'
            }, status=400)
        
        # Create bookings for each session
        created_bookings = []
        total_price = 0
        
        for session in sessions:
            # Check if session is already booked
            existing_booking = Booking.objects.filter(
                court=court,
                booking_date=booking_date_obj,
                session=session,
                booking_status__in=['pending', 'confirmed']
            ).exists()
            
            if existing_booking:
                return JsonResponse({
                    'success': False,
                    'message': f'Session {session.session_name} is already booked for this date'
                }, status=400)
            
            # Calculate duration and price
            start_time = session.start_time
            end_time = session.end_time
            
            # Calculate duration in hours
            start_datetime = datetime.combine(booking_date_obj, start_time)
            end_datetime = datetime.combine(booking_date_obj, end_time)
            duration = (end_datetime - start_datetime).total_seconds() / 3600
            
            price = Decimal(str(court.price_per_hour)) * Decimal(str(duration))
            total_price += price
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                court=court,
                session=session,
                booking_date=booking_date_obj,
                start_time=start_time,
                end_time=end_time,
                duration_hours=Decimal(str(duration)),
                total_price=price,
                booking_status='confirmed' if auto_confirm else 'pending',
                payment_status='paid' if auto_confirm else 'unpaid',
                notes=notes
            )
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=price,
                payment_method=payment_method,
                transaction_id=f'TRX-{booking.id}-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                paid_at=datetime.now() if auto_confirm else None
            )
            
            # Create Pendapatan record for mitra
            mitra = court.venue.owner  # The venue owner (mitra)
            Pendapatan.objects.create(
                mitra=mitra,
                booking=booking,
                amount=price,
                commission_rate=Decimal('10.00'),  # 10% platform commission
                payment_status='paid' if auto_confirm else 'pending',
                paid_at=datetime.now() if auto_confirm else None
            )
            
            created_bookings.append({
                'id': str(booking.id),
                'session': session.session_name,
                'start_time': str(start_time),
                'end_time': str(end_time),
                'price': float(price)
            })
        
        # Log the activity
        ActivityLog.objects.create(
            user=request.user,
            action_type='create',
            description=f'Created {len(created_bookings)} booking(s) for {court.venue.name} - {court.name}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Booking created successfully',
            'data': {
                'bookings': created_bookings,
                'total_price': float(total_price),
                'status': 'confirmed' if auto_confirm else 'pending'
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# User Booking History API
@require_http_methods(["GET"])
def api_user_booking_history(request):
    """API endpoint for getting user's booking history"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    if request.user.role != 'user':
        return JsonResponse({
            'success': False,
            'message': 'This endpoint is for users only'
        }, status=403)
    
    try:
        # Get filter parameters
        status_filter = request.GET.get('status', 'all')  # all, pending, confirmed, completed, cancelled
        sort_by = request.GET.get('sort', '-created_at')  # -created_at, booking_date, -booking_date
        limit = request.GET.get('limit', None)  # Limit number of results
        
        # Get all bookings for the user
        bookings_qs = Booking.objects.filter(user=request.user).select_related(
            'court', 'court__venue', 'session', 'payment'
        ).prefetch_related('court__images', 'court__venue__images')
        
        # Apply status filter
        if status_filter != 'all':
            bookings_qs = bookings_qs.filter(booking_status=status_filter)
        
        # Apply sorting
        valid_sorts = ['-created_at', 'created_at', 'booking_date', '-booking_date', '-updated_at', 'updated_at']
        if sort_by in valid_sorts:
            bookings_qs = bookings_qs.order_by(sort_by)
        else:
            bookings_qs = bookings_qs.order_by('-created_at')
        
        # Apply limit if provided
        if limit:
            try:
                limit = int(limit)
                bookings_qs = bookings_qs[:limit]
            except (ValueError, TypeError):
                pass
        
        # Prepare booking list
        bookings_data = []
        for booking in bookings_qs:
            # Get payment info if exists
            payment_info = None
            if hasattr(booking, 'payment'):
                payment_info = {
                    'method': booking.payment.payment_method,
                    'status': booking.payment_status,
                    'paid_at': booking.payment.paid_at.isoformat() if booking.payment.paid_at else None
                }
            
            # Get court/venue image
            court_image = None
            venue_image = None
            
            # Try to get primary court image first
            if booking.court.images.exists():
                primary_court_image = booking.court.images.filter(is_primary=True).first()
                if primary_court_image:
                    court_image = primary_court_image.image_url
                else:
                    # Get first image if no primary image
                    court_image = booking.court.images.first().image_url
            
            # Try to get primary venue image as fallback
            if not court_image and booking.court.venue.images.exists():
                primary_venue_image = booking.court.venue.images.filter(is_primary=True).first()
                if primary_venue_image:
                    venue_image = primary_venue_image.image_url
                else:
                    # Get first image if no primary image
                    venue_image = booking.court.venue.images.first().image_url
            
            bookings_data.append({
                'id': str(booking.id),
                'venue_name': booking.court.venue.name,
                'venue_id': str(booking.court.venue.id),
                'court_name': booking.court.name,
                'court_id': booking.court.id,
                'session_name': booking.session.session_name if booking.session else 'N/A',
                'session_id': booking.session.id if booking.session else None,
                'booking_date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'duration_hours': str(booking.duration_hours),
                'total_price': str(booking.total_price),
                'booking_status': booking.booking_status,
                'payment_status': booking.payment_status,
                'notes': booking.notes,
                'created_at': booking.created_at.isoformat(),
                'updated_at': booking.updated_at.isoformat(),
                'payment': payment_info,
                'is_cancellable': booking.booking_date > date.today() and booking.booking_status != 'cancelled',
                'court_image': court_image,
                'venue_image': venue_image
            })
        
        # Get statistics
        total_bookings = Booking.objects.filter(user=request.user).count()
        pending_count = Booking.objects.filter(user=request.user, booking_status='pending').count()
        confirmed_count = Booking.objects.filter(user=request.user, booking_status='confirmed').count()
        completed_count = Booking.objects.filter(user=request.user, booking_status='completed').count()
        cancelled_count = Booking.objects.filter(user=request.user, booking_status='cancelled').count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'bookings': bookings_data,
                'statistics': {
                    'total': total_bookings,
                    'pending': pending_count,
                    'confirmed': confirmed_count,
                    'completed': completed_count,
                    'cancelled': cancelled_count
                },
                'filter': status_filter,
                'sort': sort_by
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def cancel_booking(request, booking_id):
    """
    Cancel a booking - clean implementation
    Accepts both DELETE and POST methods for better compatibility
    """
    # Check authentication
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    try:
        # Get the booking
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Check if user owns this booking
        if booking.user != request.user:
            return JsonResponse({
                'success': False,
                'message': 'You are not authorized to cancel this booking'
            }, status=403)
        
        # Check if booking is already cancelled
        if booking.booking_status == 'cancelled':
            return JsonResponse({
                'success': False,
                'message': 'Booking is already cancelled'
            }, status=400)
        
        # Check if booking can be cancelled (must be before booking date)
        if booking.booking_date <= date.today():
            return JsonResponse({
                'success': False,
                'message': 'Cannot cancel booking on or after the booking date'
            }, status=400)
        
        # Get cancellation reason if provided
        cancellation_reason = ''
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode('utf-8'))
                cancellation_reason = data.get('reason', '')
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If JSON parsing fails, continue without reason
                pass
        
        # Update booking status
        booking.booking_status = 'cancelled'
        booking.cancellation_reason = cancellation_reason
        booking.updated_at = timezone.now()
        
        # If payment was made, mark for refund
        if booking.payment_status == 'paid':
            booking.payment_status = 'refunded'
            
            # Update corresponding Pendapatan record
            try:
                pendapatan = Pendapatan.objects.get(booking=booking)
                pendapatan.payment_status = 'refunded'
                pendapatan.save()
            except Pendapatan.DoesNotExist:
                print(f'Warning: No Pendapatan record found for booking {booking.id}')
        
        # Save the booking
        booking.save()
        
        # Log the cancellation activity
        try:
            ActivityLog.objects.create(
                user=request.user,
                action_type='cancel',
                description=f'Booking cancelled: {booking.court.venue.name} - {booking.court.name} on {booking.booking_date}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception as log_error:
            print(f'Failed to log cancellation activity: {log_error}')
        
        return JsonResponse({
            'success': True,
            'message': 'Booking has been successfully cancelled',
            'data': {
                'booking_id': str(booking.id),
                'booking_status': booking.booking_status,
                'payment_status': booking.payment_status,
                'cancelled_at': booking.updated_at.isoformat()
            }
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking not found'
        }, status=404)
        
    except Exception as e:
        print(f'Error cancelling booking {booking_id}: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'Failed to cancel booking: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_booking_status(request, booking_id):
    """
    Get current status of a booking
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Authentication required'
        }, status=401)
    
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Check if user owns this booking
        if booking.user != request.user:
            return JsonResponse({
                'success': False,
                'message': 'You are not authorized to view this booking'
            }, status=403)
        
        # Check if booking can be cancelled
        is_cancellable = (
            booking.booking_date > date.today() and 
            booking.booking_status not in ['cancelled', 'completed']
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'booking_id': str(booking.id),
                'venue_name': booking.court.venue.name,
                'court_name': booking.court.name,
                'booking_date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'booking_status': booking.booking_status,
                'payment_status': booking.payment_status,
                'total_price': str(booking.total_price),
                'is_cancellable': is_cancellable,
                'cancellation_reason': booking.cancellation_reason
            }
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking not found'
        }, status=404)
        
    except Exception as e:
        print(f'Error getting booking status {booking_id}: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'Failed to get booking status: {str(e)}'
        }, status=500)
