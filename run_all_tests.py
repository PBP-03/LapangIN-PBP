#!/usr/bin/env python
"""
Run all tests for the Django project
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lapangin.settings')
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Explicitly list all test modules
    test_labels = [
        'app.admin.tests',
        'app.mitra.tests',
        'app.main.tests',
        'app.users.tests',
        'app.venues.tests',
        'app.courts.tests',
        'app.bookings.tests',
        'app.reviews.tests',
        'app.revenue.tests',
    ]
    
    failures = test_runner.run_tests(test_labels)
    sys.exit(bool(failures))
