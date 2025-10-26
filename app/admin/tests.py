from django.test import TestCase, Client
from django.urls import reverse
from app.users.models import User
from django.core.exceptions import PermissionDenied


class AdminViewsTestCase(TestCase):
    """Test cases for admin views with role-based access control"""
    
    def setUp(self):
        """Set up test client and users with different roles"""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='admin123',
            email='admin@test.com',
            role='admin'
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user_test',
            password='user123',
            email='user@test.com',
            role='user'
        )
        
        # Create mitra user
        self.mitra_user = User.objects.create_user(
            username='mitra_test',
            password='mitra123',
            email='mitra@test.com',
            role='mitra'
        )
    
    def test_admin_dashboard_with_admin_user(self):
        """Test that admin user can access admin dashboard"""
        self.client.login(username='admin_test', password='admin123')
        response = self.client.get(reverse('main:app.admin:admin_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/admin.html')
    
    def test_admin_dashboard_with_regular_user(self):
        """Test that regular user cannot access admin dashboard"""
        self.client.login(username='user_test', password='user123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.admin:admin_dashboard'))
    
    def test_admin_dashboard_with_mitra_user(self):
        """Test that mitra user cannot access admin dashboard"""
        self.client.login(username='mitra_test', password='mitra123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.admin:admin_dashboard'))
    
    def test_admin_dashboard_without_authentication(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(reverse('main:app.admin:admin_dashboard'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_admin_mitra_with_admin_user(self):
        """Test that admin user can access admin mitra page"""
        self.client.login(username='admin_test', password='admin123')
        response = self.client.get(reverse('main:app.admin:admin_mitra'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/admin_mitra.html')
    
    def test_admin_mitra_with_regular_user(self):
        """Test that regular user cannot access admin mitra page"""
        self.client.login(username='user_test', password='user123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.admin:admin_mitra'))
    
    def test_admin_mitra_with_mitra_user(self):
        """Test that mitra user cannot access admin mitra page"""
        self.client.login(username='mitra_test', password='mitra123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.admin:admin_mitra'))
    
    def test_admin_mitra_without_authentication(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(reverse('main:app.admin:admin_mitra'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_admin_mitra_earnings_with_admin_user(self):
        """Test that admin user can access admin mitra earnings page"""
        self.client.login(username='admin_test', password='admin123')
        response = self.client.get(reverse('main:app.admin:admin_mitra_earnings'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/admin_mitra_earnings.html')
    
    def test_admin_mitra_earnings_with_regular_user(self):
        """Test that regular user cannot access admin mitra earnings page"""
        self.client.login(username='user_test', password='user123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.admin:admin_mitra_earnings'))
    
    def test_admin_mitra_earnings_with_mitra_user(self):
        """Test that mitra user cannot access admin mitra earnings page"""
        self.client.login(username='mitra_test', password='mitra123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.admin:admin_mitra_earnings'))
    
    def test_admin_mitra_earnings_without_authentication(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(reverse('main:app.admin:admin_mitra_earnings'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_all_admin_views_require_admin_role(self):
        """Test that all admin views require admin role"""
        # Test with admin user - all should succeed
        self.client.login(username='admin_test', password='admin123')
        
        admin_urls = [
            reverse('main:app.admin:admin_dashboard'),
            reverse('main:app.admin:admin_mitra'),
            reverse('main:app.admin:admin_mitra_earnings'),
        ]
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, 
                           f"Admin user should access {url}")
        
        self.client.logout()
        
        # Test with regular user - all should fail
        self.client.login(username='user_test', password='user123')
        
        for url in admin_urls:
            with self.assertRaises(PermissionDenied, 
                                 msg=f"Regular user should not access {url}"):
                self.client.get(url)
    
    def test_admin_dashboard_root_path(self):
        """Test that admin root path works"""
        self.client.login(username='admin_test', password='admin123')
        response = self.client.get(reverse('main:app.admin:admin'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/admin.html')
