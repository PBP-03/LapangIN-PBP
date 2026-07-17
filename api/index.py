"""WSGI entrypoint for Vercel's Python runtime.

Vercel's @vercel/python builder loads this module and looks for a
WSGI-callable named `app`. Django's own wsgi.py exposes `application`
instead, so this file just wires the two together.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lapangin.settings')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
