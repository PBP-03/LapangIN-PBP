from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from app.users.models import User
from app.venues.models import Venue, SportsCategory
from app.courts.models import Court


class MitraViewsTestCase(TestCase):
    """Test cases for mitra views with role-based access control"""
    
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
        
        # Create a category for testing
        self.category = SportsCategory.objects.create(
            name='FUTSAL',
            description='Futsal court'
        )
        
        # Create a venue for the mitra user
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra_user,
            address='Test Address',
            contact='08123456789',
            number_of_courts=1,
            verification_status='approved'
        )
        
        # Create a court for testing lapangan_detail
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=100000,
            is_active=True
        )
    
    def test_mitra_dashboard_with_mitra_user(self):
        """Test that mitra user can access mitra dashboard"""
        self.client.login(username='mitra_test', password='mitra123')
        response = self.client.get(reverse('main:app.mitra:mitra_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/mitra.html')
    
    def test_mitra_dashboard_with_admin_user(self):
        """Test that admin user cannot access mitra dashboard"""
        self.client.login(username='admin_test', password='admin123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.mitra:mitra_dashboard'))
    
    def test_mitra_dashboard_with_regular_user(self):
        """Test that regular user cannot access mitra dashboard"""
        self.client.login(username='user_test', password='user123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.mitra:mitra_dashboard'))
    
    def test_mitra_dashboard_without_authentication(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(reverse('main:app.mitra:mitra_dashboard'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_venues_list_with_mitra_user(self):
        """Test that mitra user can access venues list page"""
        self.client.login(username='mitra_test', password='mitra123')
        response = self.client.get(reverse('main:app.mitra:venues_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mitra/venues.html')
    
    def test_venues_list_with_regular_user(self):
        """Test that regular user cannot access venues list page"""
        self.client.login(username='user_test', password='user123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.mitra:venues_list'))
    
    def test_venues_list_without_authentication(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(reverse('main:app.mitra:venues_list'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_lapangan_list_with_mitra_user(self):
        """Test that mitra user can access lapangan list page"""
        self.client.login(username='mitra_test', password='mitra123')
        response = self.client.get(reverse('main:app.mitra:lapangan_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mitra/lapangan.html')
    
    def test_lapangan_list_with_regular_user(self):
        """Test that regular user cannot access lapangan list page"""
        self.client.login(username='user_test', password='user123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.mitra:lapangan_list'))
    
    def test_lapangan_list_without_authentication(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(reverse('main:app.mitra:lapangan_list'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_pendapatan_with_mitra_user(self):
        """Test that mitra user can access pendapatan page"""
        self.client.login(username='mitra_test', password='mitra123')
        response = self.client.get(reverse('main:app.mitra:pendapatan'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mitra/pendapatan.html')
    
    def test_pendapatan_with_regular_user(self):
        """Test that regular user cannot access pendapatan page"""
        self.client.login(username='user_test', password='user123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.mitra:pendapatan'))
    
    def test_pendapatan_without_authentication(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(reverse('main:app.mitra:pendapatan'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_bookings_with_mitra_user(self):
        """Test that mitra user can access bookings page"""
        self.client.login(username='mitra_test', password='mitra123')
        response = self.client.get(reverse('main:app.mitra:bookings'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mitra/bookings.html')
    
    def test_bookings_with_regular_user(self):
        """Test that regular user cannot access bookings page"""
        self.client.login(username='user_test', password='user123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.mitra:bookings'))
    
    def test_bookings_without_authentication(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(reverse('main:app.mitra:bookings'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_lapangan_detail_with_mitra_user(self):
        """Test that mitra user can access lapangan detail page"""
        self.client.login(username='mitra_test', password='mitra123')
        response = self.client.get(reverse('main:app.mitra:lapangan_detail', args=[self.court.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mitra/lapangan_detail.html')
        self.assertIn('lapangan_id', response.context)
        self.assertEqual(response.context['lapangan_id'], self.court.id)
    
    def test_lapangan_detail_with_regular_user(self):
        """Test that regular user cannot access lapangan detail page"""
        self.client.login(username='user_test', password='user123')
        
        with self.assertRaises(PermissionDenied):
            response = self.client.get(reverse('main:app.mitra:lapangan_detail', args=[self.court.id]))
    
    def test_lapangan_detail_without_authentication(self):
        """Test that unauthenticated user is redirected to login"""
        response = self.client.get(reverse('main:app.mitra:lapangan_detail', args=[self.court.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_all_mitra_views_require_mitra_role(self):
        """Test that all mitra views require mitra role"""
        # Test with mitra user - all should succeed
        self.client.login(username='mitra_test', password='mitra123')
        
        mitra_urls = [
            reverse('main:app.mitra:mitra_dashboard'),
            reverse('main:app.mitra:venues_list'),
            reverse('main:app.mitra:lapangan_list'),
            reverse('main:app.mitra:pendapatan'),
            reverse('main:app.mitra:bookings'),
            reverse('main:app.mitra:lapangan_detail', args=[self.court.id]),
        ]
        
        for url in mitra_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, 
                           f"Mitra user should access {url}")
        
        self.client.logout()
        
        # Test with regular user - all should fail
        self.client.login(username='user_test', password='user123')
        
        for url in mitra_urls:
            with self.assertRaises(PermissionDenied, 
                                 msg=f"Regular user should not access {url}"):
                self.client.get(url)
        
        self.client.logout()
        
        # Test with admin user - all should fail
        self.client.login(username='admin_test', password='admin123')
        
        for url in mitra_urls:
            with self.assertRaises(PermissionDenied, 
                                 msg=f"Admin user should not access {url}"):
                self.client.get(url)

