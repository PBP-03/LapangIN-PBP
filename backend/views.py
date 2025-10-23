from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.db.models import Sum, Count, Q
from decimal import Decimal
import json
from .models import User, ActivityLog, Venue, Court, Pendapatan, SportsCategory, Booking, Payment, CourtSession
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomLoginForm, CustomUserCreationForm, VenueForm, CourtForm
from .decorators import login_required, role_required, anonymous_required

# Create your views here.

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

            data.append({
                'id': str(m.id),
                'nama': m.get_full_name() or m.first_name or m.username,
                'email': m.email,
                'deskripsi': m.address or '',
                'gambar': m.profile_picture or '',
                'tanggal_daftar': m.created_at.isoformat() if hasattr(m, 'created_at') else None,
                'status': status,
            })

        return JsonResponse({'status': 'ok', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
def api_mitra_update_status(request, mitra_id):
    """Patch endpoint to update mitra status. Body: {"status": "approved"|"rejected"} """
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
        if new_status not in ['approved', 'rejected']:
            return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)

        if new_status == 'approved':
            mitra.is_verified = True
            mitra.is_active = True
        else:  # rejected
            mitra.is_verified = False
            # mark as inactive to reflect rejection without changing models
            mitra.is_active = False

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
                    from .models import VenueImage
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
                
                # Handle new image URLs (JSON array of URLs)
                image_urls_str = request.POST.get('image_urls', '')
                if image_urls_str:
                    try:
                        image_urls = json.loads(image_urls_str)
                        from .models import VenueImage
                        for idx, url in enumerate(image_urls):
                            if url and url.strip():
                                # If this is the first image and venue has no primary image, make it primary
                                is_primary = (idx == 0 and not venue.images.filter(is_primary=True).exists())
                                VenueImage.objects.create(
                                    venue=venue,
                                    image_url=url.strip(),
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
                    from .models import CourtImage
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
                import json
                sessions_json = request.POST.get('sessions', '[]')
                try:
                    sessions = json.loads(sessions_json)
                    from .models import CourtSession
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
        from .models import CourtSession
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
                
                # Handle new image URLs (JSON array of URLs)
                image_urls_str = request.POST.get('image_urls', '')
                if image_urls_str:
                    try:
                        image_urls = json.loads(image_urls_str)
                        from .models import CourtImage
                        for idx, url in enumerate(image_urls):
                            if url and url.strip():
                                # If this is the first image and court has no primary image, make it primary
                                is_primary = (idx == 0 and not court.images.filter(is_primary=True).exists())
                                CourtImage.objects.create(
                                    court=court,
                                    image_url=url.strip(),
                                    is_primary=is_primary
                                )
                    except (json.JSONDecodeError, ValueError):
                        pass  # Continue without images if parsing fails
                
                # Handle session slots update
                import json
                sessions_json = request.POST.get('sessions', '[]')
                try:
                    sessions = json.loads(sessions_json)
                    from .models import CourtSession
                    
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


@require_http_methods(["GET"])
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
        from .models import VenueImage
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
        from .models import CourtImage
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
