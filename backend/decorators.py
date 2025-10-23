from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied


def login_required(view_func=None, login_url='/login'):
    """
    Custom login required decorator that redirects to custom login page
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                messages.info(request, 'Silakan login terlebih dahulu.')
                return redirect(login_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func:
        return decorator(view_func)
    return decorator


def role_required(allowed_roles):
    """
    Decorator to restrict access based on user roles
    Usage: @role_required(['user', 'mitra']) or @role_required('admin')
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                messages.info(request, 'Silakan login terlebih dahulu.')
                return redirect('/login')
            
            if request.user.role not in allowed_roles:
                # For AJAX/JSON requests return 403 JSON, otherwise redirect to login with message
                if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini. Silakan login sebagai admin.')
                return redirect('/login')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def user_required(view_func):
    """Decorator for user-only views"""
    return role_required('user')(view_func)


def mitra_required(view_func):
    """Decorator for mitra-only views"""
    return role_required('mitra')(view_func)


def admin_required(view_func):
    """Decorator for admin-only views"""
    return role_required('admin')(view_func)


def anonymous_required(redirect_url='/'):
    """
    Decorator to restrict access to anonymous users only
    Useful for login/register pages
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Redirect based on user role
                if request.user.role == 'admin':
                    return redirect('/admin/dashboard')
                elif request.user.role == 'mitra':
                    return redirect('/mitra/dashboard')
                else:
                    return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator