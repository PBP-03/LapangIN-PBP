from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count, Q, Avg
import json

# Import models
from .models import User
from app.revenue.models import ActivityLog
from app.bookings.models import Booking

# Import forms
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from .utils import get_client_ip


def index(request):
    return JsonResponse({'status': 'success', 'message': 'Users API is running'})


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
                # 'role' : user.role
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
    """Check if user is authenticated and return user data"""
    if request.user.is_authenticated:
        return JsonResponse({
            'success': True,
            'authenticated': True,
            'user': {
                'id': str(request.user.id),
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'role': request.user.role,
                'profile_picture': request.user.profile_picture
            }
        })
    else:
        return JsonResponse({
            'success': True,
            'authenticated': False
        })


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
            'profile_picture': user.profile_picture,
            'created_at': user.created_at.isoformat() if getattr(user, 'created_at', None) else None,
        }
        return JsonResponse({'success': True, 'data': {'user': user_data}})

    # Update
    if request.method == 'PUT':
        try:
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
                    'profile_picture': user.profile_picture,
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

