from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Avg
import json

from app.venues.models import Venue, SportsCategory, VenueFacility, Facility, OperationalHour
from app.users.forms import VenueForm
from app.revenue.models import ActivityLog
from app.reviews.models import Review
from app.courts.models import Court
from app.users.decorators import login_required, role_required

def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Venue List & Search API
@require_http_methods(["GET"])
def api_venue_list(request):
    """API endpoint for venue list & search/filter"""
    # Get query params
    search = request.GET.get('search')  # General search parameter
    name = request.GET.get('name')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    location = request.GET.get('location')
    
    # Pagination params
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 9))

    venues = Venue.objects.filter(verification_status='approved').order_by('-created_at', 'name')
    
    # General search across multiple fields
    if search:
        venues = venues.filter(
            Q(name__icontains=search) |
            Q(address__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Specific field searches
    if name:
        venues = venues.filter(name__icontains=name)
    if category:
        venues = venues.filter(courts__category__name=category).distinct()
    if min_price:
        venues = venues.filter(courts__price_per_hour__gte=min_price).distinct()
    if max_price:
        venues = venues.filter(courts__price_per_hour__lte=max_price).distinct()
    if location:
        venues = venues.filter(address__icontains=location)

    # Get total count before pagination
    total_count = venues.count()
    
    # Calculate pagination
    total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
    offset = (page - 1) * page_size
    
    # Apply pagination
    venues = venues[offset:offset + page_size]

    data = []
    for v in venues:
        images = [img.image_url for img in v.images.all()]
        avg_rating = Review.objects.filter(booking__court__venue=v).aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Get all unique categories from courts in this venue
        courts = Court.objects.filter(venue=v).select_related('category')
        categories = set()
        total_price = 0
        court_count = 0
        for court in courts:
            if court.category:
                categories.add(court.category.get_name_display())
            total_price += float(court.price_per_hour)
            court_count += 1
        
        categories_display = ', '.join(sorted(categories)) if categories else ''
        avg_price = total_price / court_count if court_count > 0 else 0
        
        # Get venue facilities
        facilities = [
            {
                'name': vf.facility.name,
                'icon': vf.facility.icon
            } for vf in VenueFacility.objects.filter(venue=v).select_related('facility')
        ]
        
        data.append({
            'id': str(v.id),
            'name': v.name,
            'category': categories_display,
            'category_icon': None,  # Venue model doesn't have category field
            'address': v.address,
            'location_url': v.location_url,
            'contact': v.contact,
            'price_per_hour': float(avg_price),
            'number_of_courts': v.number_of_courts,
            'images': images,
            'avg_rating': round(avg_rating, 1),
            'rating_count': Review.objects.filter(booking__court__venue=v).count(),
            'facilities': facilities,
        })
    
    return JsonResponse({
        'status': 'ok', 
        'data': data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        }
    })

# Public Venue Detail API (no authentication required)
@require_http_methods(["GET"])
def api_public_venue_detail(request, venue_id):
    try:
        v = Venue.objects.get(pk=venue_id, verification_status='approved')
        
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
        courts = []
        for c in v.courts.all():
            # Get sessions for this court
            sessions = [
                {
                    'id': s.id,
                    'session_name': s.session_name,
                    'start_time': str(s.start_time),
                    'end_time': str(s.end_time),
                    'is_active': s.is_active
                } for s in c.sessions.all()
            ]
            courts.append({
                'id': c.id,
                'name': c.name,
                'is_active': c.is_active,
                'price_per_hour': float(c.price_per_hour),
                'sessions': sessions
            })
        
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
            'address': v.address,
            'location_url': v.location_url,
            'contact': v.contact,
            'description': v.description,
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
        return JsonResponse({'status': 'error', 'message': 'Venue not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
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
            
            # Get venue facilities
            facilities = []
            for vf in VenueFacility.objects.filter(venue=venue).select_related('facility'):
                facilities.append({
                    'id': vf.facility.id,
                    'name': vf.facility.name,
                    'icon': vf.facility.icon
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
                'images': images,
                'facilities': facilities
            })
        
        return JsonResponse({
            'success': True,
            'data': venues_data
        })
    
    elif request.method == 'POST':
        # Create a new venue
        try:
            # Try to parse JSON body first (from Flutter)
            try:
                body = json.loads(request.body)
                # Create venue from JSON data
                venue = Venue(
                    owner=request.user,
                    name=body.get('name', ''),
                    address=body.get('address', ''),
                    location_url=body.get('location_url', ''),
                    contact=body.get('contact', ''),
                    description=body.get('description', ''),
                    number_of_courts=0
                )
                venue.save()

                # Handle image URLs (list or JSON string)
                image_urls_data = body.get('image_urls', [])
                try:
                    if isinstance(image_urls_data, str):
                        image_urls = json.loads(image_urls_data)
                    else:
                        image_urls = image_urls_data

                    from app.venues.models import VenueImage
                    for idx, url in enumerate(image_urls or []):
                        if url and str(url).strip():
                            VenueImage.objects.create(
                                venue=venue,
                                image_url=str(url).strip(),
                                is_primary=(idx == 0),
                            )
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass  # Continue without images if parsing fails

                # Handle facilities (list or JSON string)
                facilities_data = body.get('facilities', [])
                try:
                    if isinstance(facilities_data, str):
                        facilities = json.loads(facilities_data)
                    else:
                        facilities = facilities_data

                    for facility_data in facilities or []:
                        if not isinstance(facility_data, dict):
                            continue
                        if facility_data.get('name'):
                            facility, created = Facility.objects.get_or_create(
                                name=facility_data['name'],
                                defaults={'icon': facility_data.get('icon', '')}
                            )
                            if (
                                not created
                                and facility_data.get('icon')
                                and facility.icon != facility_data.get('icon')
                            ):
                                facility.icon = facility_data.get('icon')
                                facility.save()
                            VenueFacility.objects.get_or_create(
                                venue=venue,
                                facility=facility
                            )
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass  # Continue without facilities if parsing fails
                
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
            except (json.JSONDecodeError, KeyError):
                # Fall back to form data handling (for web forms)
                pass
            
            # Handle form data
            form = VenueForm(request.POST)
            
            if form.is_valid():
                venue = form.save(commit=False)
                venue.owner = request.user
                # Set initial number_of_courts to 0 (will be updated when courts are added)
                venue.number_of_courts = 0
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
                
                # Handle facilities (JSON array of facility objects)
                facilities_str = request.POST.get('facilities', '[]')
                try:
                    facilities = json.loads(facilities_str)
                    for facility_data in facilities:
                        if facility_data.get('name'):
                            # Get or create facility
                            facility, created = Facility.objects.get_or_create(
                                name=facility_data['name'],
                                defaults={'icon': facility_data.get('icon', '')}
                            )
                            # If facility exists but icon is different, update it
                            if not created and facility_data.get('icon') and facility.icon != facility_data.get('icon'):
                                facility.icon = facility_data.get('icon')
                                facility.save()
                            # Create venue-facility relationship
                            VenueFacility.objects.get_or_create(
                                venue=venue,
                                facility=facility
                            )
                except (json.JSONDecodeError, ValueError):
                    pass  # Continue without facilities if parsing fails
                
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


@csrf_exempt
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
    
    # Handle method override from Flutter (JSON body with _method field)
    actual_method = request.method
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            if body.get('_method'):
                actual_method = body.get('_method').upper()
        except:
            pass
    
    if request.method == 'GET' or actual_method == 'GET':
        # Get venue details
        # Get venue details
        # Get venue images
        images = []
        for img in venue.images.all():
            images.append({
                'id': img.id,
                'url': img.image_url,
                'is_primary': img.is_primary,
                'caption': img.caption or ''
            })
        
        # Get venue facilities
        facilities = []
        for vf in VenueFacility.objects.filter(venue=venue).select_related('facility'):
            facilities.append({
                'name': vf.facility.name,
                'icon': vf.facility.icon or ''
            })
        
        venue_data = {
            'id': str(venue.id),
            'name': venue.name,
            'address': venue.address,
            'location_url': venue.location_url or '',
            'contact': venue.contact or '',
            'description': venue.description or '',
            'number_of_courts': venue.number_of_courts,
            'verification_status': venue.verification_status,
            'is_verified': venue.is_verified,
            'created_at': venue.created_at.isoformat(),
            'updated_at': venue.updated_at.isoformat(),
            'images': images,
            'facilities': facilities
        }
        
        return JsonResponse({
            'success': True,
            'data': venue_data
        })
    
    elif actual_method in ['PUT', 'PATCH']:
        # Update venue
        try:
            # Parse JSON body
            body = json.loads(request.body)
            
            # Update basic fields
            venue.name = body.get('name', venue.name)
            venue.address = body.get('address', venue.address)
            venue.location_url = body.get('location_url', '')
            venue.contact = body.get('contact', '')
            venue.description = body.get('description', '')
            venue.save()
            
            # Handle image URLs
            image_urls_data = body.get('image_urls', '[]')
            try:
                if isinstance(image_urls_data, str):
                    image_urls = json.loads(image_urls_data)
                else:
                    image_urls = image_urls_data
                
                # Clean submitted URLs
                submitted_urls = [url.strip() for url in image_urls if url and url.strip()]
                
                # Delete images not in submitted list
                venue.images.exclude(image_url__in=submitted_urls).delete()
                
                # Get existing URLs
                existing_urls = set(venue.images.values_list('image_url', flat=True))
                
                # Add new images
                from app.venues.models import VenueImage
                for idx, url in enumerate(submitted_urls):
                    if url not in existing_urls:
                        is_primary = (idx == 0 and not venue.images.filter(is_primary=True).exists())
                        VenueImage.objects.create(
                            venue=venue,
                            image_url=url,
                            is_primary=is_primary
                        )
            except (json.JSONDecodeError, ValueError):
                pass
            
            # Handle facilities
            facilities_data = body.get('facilities', '[]')
            try:
                if isinstance(facilities_data, str):
                    facilities = json.loads(facilities_data)
                else:
                    facilities = facilities_data
                
                # Get current facility names
                current_facility_names = set(
                    VenueFacility.objects.filter(venue=venue).values_list('facility__name', flat=True)
                )
                
                # Get submitted facility names
                submitted_facility_names = set()
                for facility_data in facilities:
                    if facility_data.get('name'):
                        submitted_facility_names.add(facility_data['name'])
                        # Get or create facility
                        facility, created = Facility.objects.get_or_create(
                            name=facility_data['name'],
                            defaults={'icon': facility_data.get('icon', '')}
                        )
                        # Update icon if different
                        if not created and facility_data.get('icon') and facility.icon != facility_data.get('icon'):
                            facility.icon = facility_data.get('icon')
                            facility.save()
                        # Create venue-facility relationship
                        VenueFacility.objects.get_or_create(
                            venue=venue,
                            facility=facility
                        )
                
                # Remove facilities no longer in list
                facilities_to_remove = current_facility_names - submitted_facility_names
                if facilities_to_remove:
                    VenueFacility.objects.filter(
                        venue=venue,
                        facility__name__in=facilities_to_remove
                    ).delete()
            except (json.JSONDecodeError, ValueError):
                pass
            
            # Log activity
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
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)
    
    elif request.method == 'POST' and actual_method not in ['PUT', 'PATCH', 'DELETE']:
        # Handle form data (for web forms)
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
                
                # Handle facilities update
                facilities_str = request.POST.get('facilities', '')
                if facilities_str:
                    try:
                        facilities = json.loads(facilities_str)
                        
                        # Get current facilities
                        current_facility_names = set(
                            VenueFacility.objects.filter(venue=venue).values_list('facility__name', flat=True)
                        )
                        
                        # Get submitted facility names
                        submitted_facility_names = set()
                        for facility_data in facilities:
                            if facility_data.get('name'):
                                submitted_facility_names.add(facility_data['name'])
                                # Get or create facility
                                facility, created = Facility.objects.get_or_create(
                                    name=facility_data['name'],
                                    defaults={'icon': facility_data.get('icon', '')}
                                )
                                # If facility exists but icon is different, update it
                                if not created and facility_data.get('icon') and facility.icon != facility_data.get('icon'):
                                    facility.icon = facility_data.get('icon')
                                    facility.save()
                                # Create venue-facility relationship if doesn't exist
                                VenueFacility.objects.get_or_create(
                                    venue=venue,
                                    facility=facility
                                )
                        
                        # Remove facilities that are no longer in the list
                        facilities_to_remove = current_facility_names - submitted_facility_names
                        if facilities_to_remove:
                            VenueFacility.objects.filter(
                                venue=venue,
                                facility__name__in=facilities_to_remove
                            ).delete()
                    except (json.JSONDecodeError, ValueError):
                        pass  # Continue without facilities if parsing fails
                
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
    
    elif actual_method == 'DELETE':
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
    
    return JsonResponse({
        'success': False,
        'message': 'Method not allowed'
    }, status=405)

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

# Operational Hours API
@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_venue_operational_hours(request, venue_id):
    """API endpoint to get or create operational hours for a venue"""
    
    # Day name to number mapping
    DAY_MAP = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }
    
    # Reverse mapping
    DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    try:
        venue = Venue.objects.get(id=venue_id, owner=request.user)
    except Venue.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Venue tidak ditemukan'
        }, status=404)
    
    if request.method == 'GET':
        hours = OperationalHour.objects.filter(venue=venue).order_by('day_of_week')
        data = [{
            'id': hour.id,
            'day_of_week': DAY_NAMES[hour.day_of_week],
            'open_time': hour.open_time.strftime('%H:%M') if hour.open_time else None,
            'close_time': hour.close_time.strftime('%H:%M') if hour.close_time else None,
            'is_closed': hour.is_closed
        } for hour in hours]
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    
    elif request.method == 'POST':
        try:
            day_of_week_str = request.POST.get('day_of_week')
            open_time = request.POST.get('open_time')
            close_time = request.POST.get('close_time')
            is_closed = request.POST.get('is_closed', 'false').lower() == 'true'
            
            if not day_of_week_str:
                return JsonResponse({
                    'success': False,
                    'message': 'Hari harus diisi'
                }, status=400)
            
            # Convert day name to number
            day_of_week = DAY_MAP.get(day_of_week_str)
            if day_of_week is None:
                return JsonResponse({
                    'success': False,
                    'message': f'Hari tidak valid: {day_of_week_str}'
                }, status=400)
            
            # Create operational hour
            hour = OperationalHour.objects.create(
                venue=venue,
                day_of_week=day_of_week,
                open_time=open_time if not is_closed and open_time else None,
                close_time=close_time if not is_closed and close_time else None,
                is_closed=is_closed
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Jam operasional berhasil ditambahkan',
                'data': {
                    'id': hour.id,
                    'day_of_week': DAY_NAMES[hour.day_of_week],
                    'open_time': hour.open_time.strftime('%H:%M') if hour.open_time else None,
                    'close_time': hour.close_time.strftime('%H:%M') if hour.close_time else None,
                    'is_closed': hour.is_closed
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_venue_operational_hour_detail(request, venue_id, hour_id):
    """API endpoint to update or delete a specific operational hour"""
    
    # Day name to number mapping
    DAY_MAP = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }
    
    # Reverse mapping
    DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    try:
        venue = Venue.objects.get(id=venue_id, owner=request.user)
        hour = OperationalHour.objects.get(id=hour_id, venue=venue)
    except Venue.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Venue tidak ditemukan'
        }, status=404)
    except OperationalHour.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Jam operasional tidak ditemukan'
        }, status=404)
    
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'data': {
                'id': hour.id,
                'day_of_week': DAY_NAMES[hour.day_of_week],
                'open_time': hour.open_time.strftime('%H:%M') if hour.open_time else None,
                'close_time': hour.close_time.strftime('%H:%M') if hour.close_time else None,
                'is_closed': hour.is_closed
            }
        })
    
    elif request.method == 'PUT' or request.POST.get('_method') == 'PUT':
        try:
            day_of_week_str = request.POST.get('day_of_week')
            open_time = request.POST.get('open_time')
            close_time = request.POST.get('close_time')
            is_closed = request.POST.get('is_closed', 'false').lower() == 'true'
            
            # Convert day name to number if provided
            if day_of_week_str:
                day_of_week = DAY_MAP.get(day_of_week_str)
                if day_of_week is None:
                    return JsonResponse({
                        'success': False,
                        'message': f'Hari tidak valid: {day_of_week_str}'
                    }, status=400)
                hour.day_of_week = day_of_week
            
            hour.open_time = open_time if not is_closed and open_time else None
            hour.close_time = close_time if not is_closed and close_time else None
            hour.is_closed = is_closed
            hour.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Jam operasional berhasil diupdate',
                'data': {
                    'id': hour.id,
                    'day_of_week': DAY_NAMES[hour.day_of_week],
                    'open_time': hour.open_time.strftime('%H:%M') if hour.open_time else None,
                    'close_time': hour.close_time.strftime('%H:%M') if hour.close_time else None,
                    'is_closed': hour.is_closed
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)
    
    elif request.method == 'DELETE' or request.POST.get('_method') == 'DELETE':
        hour.delete()
        return JsonResponse({
            'success': True,
            'message': 'Jam operasional berhasil dihapus'
        })
