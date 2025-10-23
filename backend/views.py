from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import json
from .models import User, ActivityLog
from .models import Mitra
from .decorators import admin_required
from .forms import CustomLoginForm, CustomUserCreationForm
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


@admin_required
def admin_mitra_page(request):
    """Render admin page for managing mitra (template only)"""
    from django.shortcuts import render
    return render(request, 'admin_mitra.html')


def api_admin_mitra_redirect(request):
    """Redirect API path /api/admin/mitra/ to the HTML admin page /admin/mitra/"""
    return redirect('/admin/mitra/')


@csrf_exempt
@require_http_methods(["GET"])
def mitra_list(request):
    """Return JSON list of all mitra"""
    mitras = Mitra.objects.all().order_by('-tanggal_daftar')
    data = [
        {
            'id': m.id,
            'nama': m.nama,
            'email': m.email,
            'status': m.status,
            'tanggal_daftar': m.tanggal_daftar.isoformat(),
        }
        for m in mitras
    ]
    return JsonResponse({'status': 'ok', 'data': data})


@csrf_exempt
@require_http_methods(["PATCH"])
def mitra_detail(request, pk):
    """Patch mitra status"""
    try:
        mitra = Mitra.objects.get(pk=pk)
    except Mitra.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Mitra not found'}, status=404)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        payload = {}

    new_status = payload.get('status')
    if new_status not in [Mitra.STATUS_APPROVED, Mitra.STATUS_REJECTED]:
        return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)

    mitra.status = new_status
    mitra.save()
    return JsonResponse({'status': 'ok', 'message': f'Mitra {new_status} successfully', 'data': {'id': mitra.id, 'status': mitra.status}})