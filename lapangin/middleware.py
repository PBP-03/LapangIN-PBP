"""
Custom middleware and utilities for LapangIN project.
"""
from django.views.static import serve as static_serve
from django.http import HttpResponse, Http404
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.views import serve as staticfiles_serve
from functools import wraps
import os


def add_cors_headers(headers, path, url):
    """
    Function to add CORS headers to static files served by WhiteNoise.
    This allows images and other static files to be loaded from different origins.
    
    Args:
        headers: Dictionary of response headers
        path: File path being served
        url: URL of the file
    """
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    headers['Access-Control-Allow-Headers'] = '*'
    return headers  # WhiteNoise expects the function to return headers


def cors_static_serve(request, path, insecure=False, **kwargs):
    """
    Serve static files with CORS headers for cross-origin requests.
    Uses Django's staticfiles finders to locate files from all configured sources.
    """
    # Handle OPTIONS preflight requests
    if request.method == 'OPTIONS':
        response = HttpResponse(status=200)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response['Access-Control-Allow-Headers'] = '*'
        response['Access-Control-Max-Age'] = '86400'
        response['Content-Length'] = '0'
        print(f"[cors_static_serve] OPTIONS request for: {path}")
        return response
    
    try:
        print(f"[cors_static_serve] Serving: {path}")
        
        # Use Django's staticfiles serve which finds files from all static locations
        response = staticfiles_serve(request, path, insecure=True)
        
        # Add CORS headers to the response
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response['Access-Control-Allow-Headers'] = '*'
        response['Access-Control-Expose-Headers'] = '*'
        
        # Ensure proper Content-Type for images
        import mimetypes
        if not response.get('Content-Type'):
            content_type, encoding = mimetypes.guess_type(path)
            if content_type:
                response['Content-Type'] = content_type
        
        # Log image serving details
        if path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            content_length = response.get('Content-Length', 'unknown')
            content_type = response.get('Content-Type', 'unknown')
            print(f"  ✓ Content-Type: {content_type}, Content-Length: {content_length} bytes")
        
        return response
    except Exception as e:
        print(f"[cors_static_serve] ✗ Error serving {path}: {str(e)}")
        raise


class ManualCookieMiddleware:
    """
    Middleware to manually extract cookies from the Cookie header.
    This is needed for Flutter Web where the http package sends cookies in the header
    but Django doesn't automatically parse them into request.COOKIES.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for Authorization header with auth token (for Flutter Web)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            import base64
            from django.contrib.sessions.models import Session
            from django.contrib.auth import get_user_model
            
            try:
                token = auth_header.split('Bearer ')[1]
                decoded = base64.b64decode(token).decode()
                user_id, session_id = decoded.split(':', 1)
                
                # Set the session ID in cookies so Django's SessionMiddleware can load it
                request.COOKIES['sessionid'] = session_id
                print(f"[ManualCookieMiddleware] Restored session from auth token: {session_id}")
            except Exception as e:
                print(f"[ManualCookieMiddleware] Failed to decode auth token: {e}")
        
        response = self.get_response(request)
        return response


class CorsStaticMiddleware:
    """
    Middleware to add CORS headers to static file responses.
    This allows images and other static files to be loaded from different origins.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle OPTIONS preflight requests IMMEDIATELY
        if request.method == 'OPTIONS':
            from django.http import HttpResponse
            response = HttpResponse(status=200)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            response['Access-Control-Allow-Headers'] = '*'
            response['Access-Control-Max-Age'] = '86400'
            response['Content-Length'] = '0'
            # Log OPTIONS requests for debugging
            print(f"[CorsStaticMiddleware] OPTIONS request for: {request.path}")
            return response
        
        response = self.get_response(request)
        
        # Add CORS headers for ALL requests to allow cross-origin access
        # This is especially important for static files and images
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response['Access-Control-Allow-Headers'] = '*'
        response['Access-Control-Expose-Headers'] = '*'
        
        # Remove Access-Control-Allow-Credentials to avoid conflicts with wildcard origin
        if 'Access-Control-Allow-Credentials' in response:
            del response['Access-Control-Allow-Credentials']
        
        return response
