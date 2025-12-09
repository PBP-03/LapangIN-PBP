from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Avg
import json

from app.venues.models import Venue, SportsCategory, VenueFacility, Facility
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
        
        # Get venue facilities
        facilities = []
        for vf in VenueFacility.objects.filter(venue=venue).select_related('facility'):
            facilities.append({
                'name': vf.facility.name,
                'icon': vf.facility.icon
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
            'images': images,
            'facilities': facilities
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
