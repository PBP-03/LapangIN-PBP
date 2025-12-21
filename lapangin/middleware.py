"""
Custom middleware for development
"""

class DevCsrfMiddleware:
    """
    Middleware to allow CSRF for localhost origins in development
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # In development, allow localhost with any port
        origin = request.META.get('HTTP_ORIGIN', '')
        if origin.startswith('http://localhost') or origin.startswith('http://127.0.0.1'):
            # Add to trusted origins dynamically
            from django.conf import settings
            if origin not in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS.append(origin)
        return None
