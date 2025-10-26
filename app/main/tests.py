from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, time
from app.users.models import User
from app.venues.models import Venue, SportsCategory, VenueImage, VenueFacility, Facility, OperationalHour
from app.courts.models import Court, CourtSession
from app.bookings.models import Booking
from app.reviews.models import Review


class MainViewsTestCase(TestCase):
    """Test cases for main views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='user@test.com',
            role='user',
            first_name='Test',
            last_name='User'
        )
        
        self.mitra = User.objects.create_user(
            username='testmitra',
            password='testpass123',
            email='mitra@test.com',
            role='mitra',
            first_name='Test',
            last_name='Mitra'
        )
        
        self.admin = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            email='admin@test.com',
            role='admin',
            first_name='Test',
            last_name='Admin'
        )
        
        # Create sports category
        self.category = SportsCategory.objects.create(
            name='FUTSAL',
            description='Futsal court'
        )
        
        # Create venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address 123',
            contact='081234567890',
            description='Test venue description',
            number_of_courts=2,
            verification_status='approved'
        )
        
        # Create venue image
        self.venue_image = VenueImage.objects.create(
            venue=self.venue,
            image_url='https://example.com/image.jpg',
            is_primary=True
        )
        
        # Create facility
        self.facility = Facility.objects.create(
            name='Parking',
            description='Parking area'
        )
        
        # Add facility to venue
        VenueFacility.objects.create(
            venue=self.venue,
            facility=self.facility
        )
        
        # Create operational hours
        OperationalHour.objects.create(
            venue=self.venue,
            day_of_week=0,
            open_time=time(8, 0),
            close_time=time(22, 0)
        )
        
        # Create court
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=100000,
            is_active=True
        )
        
        # Create court session
        self.session = CourtSession.objects.create(
            court=self.court,
            session_name='Morning Session',
            start_time=time(8, 0),
            end_time=time(10, 0),
            is_active=True
        )
    
    def test_index_view(self):
        """Test index/home page"""
        response = self.client.get(reverse('main:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
    
    def test_venue_list_view(self):
        """Test venue list page"""
        response = self.client.get(reverse('main:venue_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'venue_list.html')
        self.assertIn('venues_json', response.context)
    
    def test_venue_list_view_with_search(self):
        """Test venue list page with search query"""
        response = self.client.get(reverse('main:venue_list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'venue_list.html')
        self.assertIn('search_query', response.context)
        self.assertEqual(response.context['search_query'], 'Test')
    
    def test_venue_detail_view(self):
        """Test venue detail page"""
        response = self.client.get(reverse('main:venue_detail', args=[self.venue.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'venue_detail.html')
        self.assertEqual(response.context['venue'], self.venue)
        self.assertIn('courts', response.context)
        self.assertIn('facilities', response.context)
        self.assertIn('images', response.context)
    
    def test_venue_detail_view_with_authenticated_user(self):
        """Test venue detail page with authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:venue_detail', args=[self.venue.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_authenticated'])
    
    def test_venue_detail_view_can_review_after_completed_booking(self):
        """Test that user can review after completed booking"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a completed booking
        booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            session=self.session,
            booking_date=date.today(),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=2,
            total_price=200000,
            booking_status='completed',
            payment_status='paid'
        )
        
        response = self.client.get(reverse('main:venue_detail', args=[self.venue.id]))
        self.assertTrue(response.context['can_review'])
        
        # After adding a review, can_review should be False
        Review.objects.create(
            booking=booking,
            rating=5,
            comment='Great venue!'
        )
        
        response = self.client.get(reverse('main:venue_detail', args=[self.venue.id]))
        self.assertFalse(response.context['can_review'])
    
    def test_venue_detail_404_for_nonexistent_venue(self):
        """Test venue detail returns 404 for nonexistent venue"""
        import uuid
        fake_id = uuid.uuid4()
        response = self.client.get(reverse('main:venue_detail', args=[fake_id]))
        self.assertEqual(response.status_code, 404)
    
    def test_login_view_unauthenticated(self):
        """Test login page for unauthenticated users"""
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')
    
    def test_login_view_redirects_authenticated_user(self):
        """Test login page redirects authenticated users to dashboard"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.url)
    
    def test_login_view_redirects_admin_to_admin_dashboard(self):
        """Test login page redirects admin to admin dashboard"""
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/dashboard', response.url)
    
    def test_login_view_redirects_mitra_to_mitra_dashboard(self):
        """Test login page redirects mitra to mitra dashboard"""
        self.client.login(username='testmitra', password='testpass123')
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/mitra/dashboard', response.url)
    
    def test_register_view_unauthenticated(self):
        """Test register page for unauthenticated users"""
        response = self.client.get(reverse('main:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')
    
    def test_register_view_redirects_authenticated_user(self):
        """Test register page redirects authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:register'))
        self.assertEqual(response.status_code, 302)
    
    def test_user_dashboard_requires_login(self):
        """Test user dashboard requires authentication"""
        response = self.client.get(reverse('main:user_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_user_dashboard_requires_user_role(self):
        """Test user dashboard requires user role"""
        # Login as admin
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(reverse('main:user_dashboard'))
        self.assertEqual(response.status_code, 403)
        
        # Login as mitra
        self.client.logout()
        self.client.login(username='testmitra', password='testpass123')
        response = self.client.get(reverse('main:user_dashboard'))
        self.assertEqual(response.status_code, 403)
    
    def test_user_dashboard_access_with_user_role(self):
        """Test user dashboard accessible with user role"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:user_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/user.html')
    
    def test_profile_view_requires_login(self):
        """Test profile view requires authentication"""
        response = self.client.get(reverse('main:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
    
    def test_about_view(self):
        """Test about page"""
        response = self.client.get(reverse('main:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')
    
    def test_contact_view(self):
        """Test contact page"""
        response = self.client.get(reverse('main:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')
    
    def test_daftar_mitra_view(self):
        """Test daftar mitra page"""
        response = self.client.get(reverse('main:daftar_mitra'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'daftar_mitra.html')
    
    def test_booking_checkout_view_requires_login(self):
        """Test booking checkout requires authentication"""
        response = self.client.get(reverse('main:booking_checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_booking_checkout_view_authenticated(self):
        """Test booking checkout for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:booking_checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_checkout.html')
    
    def test_booking_history_view_requires_login(self):
        """Test booking history requires authentication"""
        response = self.client.get(reverse('main:booking_history'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_booking_history_view_authenticated(self):
        """Test booking history for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:booking_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_history.html')
    
    def test_venue_list_shows_only_approved_venues(self):
        """Test venue list shows only approved venues"""
        # Create pending venue
        pending_venue = Venue.objects.create(
            name='Pending Venue',
            owner=self.mitra,
            address='Pending Address',
            number_of_courts=1,
            verification_status='pending'
        )
        
        response = self.client.get(reverse('main:venue_list'))
        self.assertEqual(response.status_code, 200)
        
        # The approved venue should be in the context
        import json
        venues_json = json.loads(response.context['venues_json'])
        venue_names = [v['name'] for v in venues_json]
        self.assertIn('Test Venue', venue_names)
        self.assertNotIn('Pending Venue', venue_names)

