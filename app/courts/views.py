from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, date

from app.courts.models import Court, CourtSession, CourtImage
from app.bookings.models import Booking
from app.users.decorators import login_required, role_required
from app.users.forms import CourtForm
from app.revenue.models import ActivityLog

def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_exempt
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


@csrf_exempt
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


def api_court_sessions(request, court_id):
    """API endpoint for getting available sessions for a specific court with booking status"""
    try:
        court = Court.objects.get(id=court_id)
        
        # Get date parameter (required for checking booking status)
        booking_date = request.GET.get('date')  # Format: YYYY-MM-DD
        
        if not booking_date:
            return JsonResponse({
                'success': False,
                'message': 'Date parameter is required'
            }, status=400)
        
        # Parse and validate date
        try:
            date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
            
            # Don't allow past dates (except today)
            if date_obj < date.today():
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot check availability for past dates'
                }, status=400)
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM-DD'
            }, status=400)
        
        # Get all active sessions for this court
        sessions = CourtSession.objects.filter(
            court=court,
            is_active=True
        ).order_by('start_time')
        
        sessions_data = []
        for session in sessions:
            # Calculate session duration in minutes
            start_time = session.start_time
            end_time = session.end_time
            
            # Calculate duration
            start_datetime = datetime.combine(date_obj, start_time)
            end_datetime = datetime.combine(date_obj, end_time)
            duration_minutes = int((end_datetime - start_datetime).total_seconds() / 60)
            
            # Check if this session is booked on the specified date
            booking = Booking.objects.filter(
                court=court,
                session=session,
                booking_date=date_obj,
                booking_status__in=['pending', 'confirmed']
            ).first()
            
            is_available = not bool(booking)
            
            session_info = {
                'id': session.id,
                'session_name': session.session_name,
                'start_time': session.start_time.strftime('%H:%M'),
                'end_time': session.end_time.strftime('%H:%M'),
                'duration': duration_minutes,
                'is_active': session.is_active,
                'is_available': is_available,
                'is_booked': bool(booking),
                'booking_id': str(booking.id) if booking else None,
                'booking_user': booking.user.get_full_name() if booking else None
            }
            
            sessions_data.append(session_info)
        
        return JsonResponse({
            'success': True,
            'status': 'ok',
            'data': {
                'court_id': court.id,
                'court_name': court.name,
                'venue_name': court.venue.name,
                'venue_id': str(court.venue.id),
                'price_per_hour': float(court.price_per_hour),
                'sessions': sessions_data,
                'date': booking_date,
                'total_sessions': len(sessions_data),
                'available_sessions': len([s for s in sessions_data if s['is_available']])
            }
        })
        
    except Court.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Court not found'
        }, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
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
