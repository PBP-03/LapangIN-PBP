from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import json
from .models import User, ActivityLog
from .forms import CustomLoginForm, CustomUserCreationForm
from .decorators import login_required, role_required, anonymous_required

# Create your views here.

def index(request):
    return JsonResponse({'status': 'success', 'message': 'Hello, world!'})


@anonymous_required()
def login_view(request):
    """Main login page that shows role selection"""
    if request.method == 'POST':
        # Handle AJAX request
        if request.content_type == 'application/json':
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
                        description=f'User {user.username} logged in',
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
        
        # Handle regular form submission (fallback)
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Log the login activity
                ActivityLog.objects.create(
                    user=user,
                    action_type='login',
                    description=f'User {user.username} logged in',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Redirect based on role
                if user.role == 'admin':
                    messages.success(request, f'Selamat datang, Admin {user.first_name}!')
                    return redirect('/admin/dashboard')
                elif user.role == 'mitra':
                    messages.success(request, f'Selamat datang, {user.first_name}!')
                    return redirect('/mitra/dashboard')
                else:
                    messages.success(request, f'Selamat datang, {user.first_name}!')
                    return redirect('/')
            else:
                messages.error(request, 'Username atau password salah.')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa input Anda.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@anonymous_required()
def register_view(request):
    """User registration page"""
    if request.method == 'POST':
        # Handle AJAX request
        if request.content_type == 'application/json':
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
                        'redirect_url': '/login'
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
        
        # Handle regular form submission (fallback)
        form = CustomUserCreationForm(request.POST)
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
            
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('/login')
        else:
            messages.error(request, 'Terjadi kesalahan pada form. Silakan periksa input Anda.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    """Logout view"""
    if request.user.is_authenticated:
        # Log the logout activity
        ActivityLog.objects.create(
            user=request.user,
            action_type='logout',
            description=f'User {request.user.username} logged out',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logout(request)
        
        # Handle AJAX request
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': 'Anda telah berhasil logout.',
                'redirect_url': '/'
            })
        
        messages.success(request, 'Anda telah berhasil logout.')
    
    return redirect('/')


@role_required('user')
def user_dashboard(request):
    """User dashboard - accessible only to users with 'user' role"""
    if request.headers.get('Accept') == 'application/json':
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
    
    return render(request, 'dashboard/user.html', {
        'user': request.user,
        'title': 'Dashboard User'
    })


@role_required('mitra')
def mitra_dashboard(request):
    """Mitra dashboard - accessible only to users with 'mitra' role"""
    # Get mitra's venues
    venues = request.user.venue_set.all()
    
    if request.headers.get('Accept') == 'application/json':
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
    
    return render(request, 'dashboard/mitra.html', {
        'user': request.user,
        'venues': venues,
        'title': 'Dashboard Mitra'
    })


@role_required('admin')
def admin_dashboard(request):
    """Admin dashboard - accessible only to users with 'admin' role"""
    # Get some statistics
    total_users = User.objects.filter(role='user').count()
    total_mitras = User.objects.filter(role='mitra').count()
    recent_activities = ActivityLog.objects.all()[:10]
    
    if request.headers.get('Accept') == 'application/json':
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
    
    return render(request, 'dashboard/admin.html', {
        'user': request.user,
        'total_users': total_users,
        'total_mitras': total_mitras,
        'recent_activities': recent_activities,
        'title': 'Dashboard Admin'
    })


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