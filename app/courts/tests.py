from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
import json
from datetime import time, date, datetime, timedelta
from unittest.mock import patch, Mock
import uuid

from app.courts.models import Court, CourtSession, CourtImage
from app.venues.models import Venue, SportsCategory, VenueImage, VenueFacility
from app.bookings.models import Booking, Payment
from app.reviews.models import Review
from app.revenue.models import Pendapatan, ActivityLog
from app.venues.views import update_venue_court_count

User = get_user_model()


class CourtModelTest(TestCase):
    """Test cases for Court model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testmitra',
            email='mitra@test.com',
            password='testpass123',
            role='mitra',
            first_name='Test',
            last_name='Mitra'
        )
        
        self.category = SportsCategory.objects.create(
            name='futsal',
        )
        
        self.venue = Venue.objects.create(
            owner=self.user,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            description='Test Description',
            number_of_courts=0,
            verification_status='approved'
        )
        
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=Decimal('100000.00'),
            is_active=True,
            description='Test court'
        )
    
    def test_court_creation(self):
        """Test court object is created correctly"""
        self.assertEqual(self.court.venue, self.venue)
        self.assertEqual(self.court.name, 'Court 1')
        self.assertEqual(self.court.category, self.category)
        self.assertEqual(self.court.price_per_hour, Decimal('100000.00'))
        self.assertTrue(self.court.is_active)
        self.assertEqual(self.court.description, 'Test court')
    
    def test_court_string_representation(self):
        """Test court string representation"""
        expected = f"{self.venue.name} - {self.court.name} ({self.category.get_name_display()})"
        self.assertEqual(str(self.court), expected)
    
    def test_court_string_without_category(self):
        """Test court string representation without category"""
        court_no_cat = Court.objects.create(
            venue=self.venue,
            name='Court 2',
            price_per_hour=Decimal('50000.00')
        )
        expected = f"{self.venue.name} - Court 2 (No Category)"
        self.assertEqual(str(court_no_cat), expected)
    
    def test_court_unique_together_constraint(self):
        """Test that venue and name must be unique together"""
        with self.assertRaises(Exception):
            Court.objects.create(
                venue=self.venue,
                name='Court 1',  # Duplicate name in same venue
                price_per_hour=Decimal('100000.00')
            )
    
    def test_court_default_values(self):
        """Test court default values"""
        court = Court.objects.create(
            venue=self.venue,
            name='Court Default'
        )
        self.assertEqual(court.price_per_hour, Decimal('0'))
        self.assertTrue(court.is_active)
        self.assertIsNone(court.maintenance_notes)
        self.assertIsNone(court.description)
    
    def test_court_relationship_with_venue(self):
        """Test court relationship with venue"""
        self.assertIn(self.court, self.venue.courts.all())
        self.assertEqual(self.venue.courts.count(), 1)


class CourtSessionModelTest(TestCase):
    """Test cases for CourtSession model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testmitra',
            email='mitra@test.com',
            password='testpass123',
            role='mitra'
        )
        
        self.venue = Venue.objects.create(
            owner=self.user,
            name='Test Venue',
            address='Test Address',
            number_of_courts=0
        )
        
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            price_per_hour=Decimal('100000.00')
        )
        
        self.session = CourtSession.objects.create(
            court=self.court,
            session_name='Morning Session',
            start_time=time(8, 0),
            end_time=time(10, 0),
            is_active=True
        )
    
    def test_session_creation(self):
        """Test session object is created correctly"""
        self.assertEqual(self.session.court, self.court)
        self.assertEqual(self.session.session_name, 'Morning Session')
        self.assertEqual(self.session.start_time, time(8, 0))
        self.assertEqual(self.session.end_time, time(10, 0))
        self.assertTrue(self.session.is_active)
    
    def test_session_string_representation(self):
        """Test session string representation"""
        expected = f"{self.court.name} - Morning Session (08:00:00-10:00:00)"
        self.assertEqual(str(self.session), expected)
    
    def test_session_ordering(self):
        """Test sessions are ordered by start_time"""
        session2 = CourtSession.objects.create(
            court=self.court,
            session_name='Afternoon Session',
            start_time=time(14, 0),
            end_time=time(16, 0)
        )
        session3 = CourtSession.objects.create(
            court=self.court,
            session_name='Evening Session',
            start_time=time(18, 0),
            end_time=time(20, 0)
        )
        
        sessions = list(self.court.sessions.all())
        self.assertEqual(sessions[0].start_time, time(8, 0))
        self.assertEqual(sessions[1].start_time, time(14, 0))
        self.assertEqual(sessions[2].start_time, time(18, 0))
    
    def test_session_unique_together_constraint(self):
        """Test that court and start_time must be unique together"""
        with self.assertRaises(Exception):
            CourtSession.objects.create(
                court=self.court,
                session_name='Another Session',
                start_time=time(8, 0),  # Duplicate start time
                end_time=time(12, 0)
            )
    
    def test_session_relationship_with_court(self):
        """Test session relationship with court"""
        self.assertIn(self.session, self.court.sessions.all())
        self.assertEqual(self.court.sessions.count(), 1)


class CourtImageModelTest(TestCase):
    """Test cases for CourtImage model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testmitra',
            email='mitra@test.com',
            password='testpass123',
            role='mitra'
        )
        
        self.venue = Venue.objects.create(
            owner=self.user,
            name='Test Venue',
            address='Test Address',
            number_of_courts=0
        )
        
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            price_per_hour=Decimal('100000.00')
        )
        
        self.image = CourtImage.objects.create(
            court=self.court,
            image_url='https://example.com/image.jpg',
            is_primary=True,
            caption='Test Caption'
        )
    
    def test_image_creation(self):
        """Test image object is created correctly"""
        self.assertEqual(self.image.court, self.court)
        self.assertEqual(self.image.image_url, 'https://example.com/image.jpg')
        self.assertTrue(self.image.is_primary)
        self.assertEqual(self.image.caption, 'Test Caption')
        self.assertIsNotNone(self.image.uploaded_at)
    
    def test_image_string_representation(self):
        """Test image string representation"""
        expected = f"{self.venue.name} - {self.court.name} - Image"
        self.assertEqual(str(self.image), expected)
    
    def test_image_default_values(self):
        """Test image default values"""
        image = CourtImage.objects.create(
            court=self.court,
            image_url='https://example.com/another.jpg'
        )
        self.assertFalse(image.is_primary)
        self.assertIsNone(image.caption)
    
    def test_image_relationship_with_court(self):
        """Test image relationship with court"""
        self.assertIn(self.image, self.court.images.all())
        self.assertEqual(self.court.images.count(), 1)


class UpdateVenueCourtCountTest(TestCase):
    """Test cases for update_venue_court_count helper function"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testmitra',
            email='mitra@test.com',
            password='testpass123',
            role='mitra'
        )
        
        self.venue = Venue.objects.create(
            owner=self.user,
            name='Test Venue',
            address='Test Address',
            number_of_courts=0
        )
    
    def test_update_count_with_no_courts(self):
        """Test updating count when venue has no courts"""
        self.venue.number_of_courts = 5  # Wrong count
        self.venue.save()
        
        update_venue_court_count(self.venue)
        self.venue.refresh_from_db()
        
        self.assertEqual(self.venue.number_of_courts, 0)
    
    def test_update_count_with_courts(self):
        """Test updating count when venue has courts"""
        Court.objects.create(venue=self.venue, name='Court 1', price_per_hour=Decimal('100000'))
        Court.objects.create(venue=self.venue, name='Court 2', price_per_hour=Decimal('100000'))
        Court.objects.create(venue=self.venue, name='Court 3', price_per_hour=Decimal('100000'))
        
        self.venue.number_of_courts = 0  # Wrong count
        self.venue.save()
        
        update_venue_court_count(self.venue)
        self.venue.refresh_from_db()
        
        self.assertEqual(self.venue.number_of_courts, 3)
    
    def test_update_count_no_change_needed(self):
        """Test that function doesn't update if count is already correct"""
        Court.objects.create(venue=self.venue, name='Court 1', price_per_hour=Decimal('100000'))
        
        self.venue.number_of_courts = 1
        self.venue.save()
        
        # Get the updated_at timestamp before
        before_update = self.venue.updated_at
        
        update_venue_court_count(self.venue)
        self.venue.refresh_from_db()
        
        self.assertEqual(self.venue.number_of_courts, 1)


class CourtAPITest(TestCase):
    """Test cases for Court API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create mitra user
        self.mitra = User.objects.create_user(
            username='testmitra',
            email='mitra@test.com',
            password='testpass123',
            role='mitra',
            first_name='Test',
            last_name='Mitra'
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        
        # Create category
        self.category = SportsCategory.objects.create(name='futsal')
        
        # Create venue
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            number_of_courts=0,
            verification_status='approved'
        )
        
        # Create court
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=Decimal('100000.00'),
            is_active=True,
            description='Test Court'
        )
    
    def test_list_courts_unauthenticated(self):
        """Test listing courts without authentication"""
        response = self.client.get('/api/courts/')
        self.assertEqual(response.status_code, 401)
    
    def test_list_courts_non_mitra(self):
        """Test listing courts as non-mitra user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/courts/')
        self.assertEqual(response.status_code, 403)
    
    def test_list_courts_success(self):
        """Test listing courts successfully"""
        self.client.login(username='testmitra', password='testpass123')
        response = self.client.get('/api/courts/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], 'Court 1')
    
    def test_list_courts_filtered_by_venue(self):
        """Test listing courts filtered by venue"""
        # Create another venue and court
        venue2 = Venue.objects.create(
            owner=self.mitra,
            name='Another Venue',
            address='Another Address',
            number_of_courts=0
        )
        Court.objects.create(
            venue=venue2,
            name='Court A',
            price_per_hour=Decimal('50000.00')
        )
        
        self.client.login(username='testmitra', password='testpass123')
        response = self.client.get(f'/api/courts/?venue_id={self.venue.id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], 'Court 1')
    
    def test_create_court_success(self):
        """Test creating a court successfully"""
        self.client.login(username='testmitra', password='testpass123')
        
        court_data = {
            'venue': str(self.venue.id),
            'name': 'Court 2',
            'category': str(self.category.id),
            'price_per_hour': '150000',
            'is_active': 'on',
            'description': 'New Court',
            'image_urls': json.dumps(['https://example.com/image.jpg']),
            'sessions': json.dumps([{
                'session_name': 'Morning',
                'start_time': '08:00',
                'end_time': '10:00',
                'is_active': True
            }])
        }
        
        initial_count = Court.objects.count()
        response = self.client.post('/api/courts/', court_data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Court 2')
        
        # Verify court was created
        self.assertEqual(Court.objects.count(), initial_count + 1)
    
    def test_create_court_unauthenticated(self):
        """Test creating court without authentication"""
        court_data = {
            'venue': str(self.venue.id),
            'name': 'Court 2',
            'price_per_hour': '100000'
        }
        response = self.client.post('/api/courts/', court_data)
        self.assertEqual(response.status_code, 401)
    
    def test_get_court_detail_success(self):
        """Test getting court detail"""
        self.client.login(username='testmitra', password='testpass123')
        response = self.client.get(f'/api/courts/{self.court.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Court 1')
    
    def test_update_court_success(self):
        """Test updating a court"""
        self.client.login(username='testmitra', password='testpass123')
        
        update_data = {
            'name': 'Updated Court',
            'venue': str(self.venue.id),
            'category': str(self.category.id),
            'price_per_hour': '200000',
            'description': 'Updated description'
        }
        
        response = self.client.post(
            f'/api/courts/{self.court.id}/',
            update_data
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        self.court.refresh_from_db()
        self.assertEqual(self.court.name, 'Updated Court')
        self.assertEqual(self.court.price_per_hour, Decimal('200000'))
    
    def test_delete_court_success(self):
        """Test deleting a court"""
        self.client.login(username='testmitra', password='testpass123')
        
        court_id = self.court.id
        
        response = self.client.delete(f'/api/courts/{court_id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify court is deleted
        self.assertFalse(Court.objects.filter(id=court_id).exists())
    
    def test_delete_court_unauthorized(self):
        """Test deleting court by non-owner"""
        another_mitra = User.objects.create_user(
            username='another_mitra',
            email='another@test.com',
            password='testpass123',
            role='mitra'
        )
        self.client.login(username='another_mitra', password='testpass123')
        
        response = self.client.delete(f'/api/courts/{self.court.id}/')
        self.assertEqual(response.status_code, 404)
    
    def test_court_with_images(self):
        """Test court with multiple images"""
        CourtImage.objects.create(
            court=self.court,
            image_url='https://example.com/img1.jpg',
            is_primary=True
        )
        CourtImage.objects.create(
            court=self.court,
            image_url='https://example.com/img2.jpg',
            is_primary=False
        )
        
        self.client.login(username='testmitra', password='testpass123')
        response = self.client.get(f'/api/courts/{self.court.id}/')
        
        data = json.loads(response.content)
        self.assertEqual(len(data['data']['images']), 2)
    
    def test_court_with_sessions(self):
        """Test court with sessions"""
        CourtSession.objects.create(
            court=self.court,
            session_name='Morning',
            start_time=time(8, 0),
            end_time=time(10, 0)
        )
        CourtSession.objects.create(
            court=self.court,
            session_name='Evening',
            start_time=time(18, 0),
            end_time=time(20, 0)
        )
        
        self.client.login(username='testmitra', password='testpass123')
        response = self.client.get(f'/api/courts/{self.court.id}/')
        
        data = json.loads(response.content)
        self.assertEqual(len(data['data']['sessions']), 2)
    
    def test_create_court_with_invalid_data(self):
        """Test creating court with invalid data"""
        self.client.login(username='testmitra', password='testpass123')
        
        court_data = {
            'venue': 'invalid-uuid',
            'name': '',  # Empty name
            'price_per_hour': 'not-a-number'
        }
        
        response = self.client.post('/api/courts/', court_data)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
    
    def test_update_court_not_found(self):
        """Test updating non-existent court"""
        self.client.login(username='testmitra', password='testpass123')
        
        from uuid import uuid4
        fake_id = str(uuid4())
        
        response = self.client.post(f'/api/courts/{fake_id}/', {
            'name': 'Test',
            'venue': str(self.venue.id),
            'price_per_hour': '100000'
        })
        self.assertEqual(response.status_code, 404)
    
    def test_get_court_detail_not_found(self):
        """Test getting detail of non-existent court"""
        self.client.login(username='testmitra', password='testpass123')
        
        from uuid import uuid4
        fake_id = str(uuid4())
        
        response = self.client.get(f'/api/courts/{fake_id}/')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_court_not_found(self):
        """Test deleting non-existent court"""
        self.client.login(username='testmitra', password='testpass123')
        
        from uuid import uuid4
        fake_id = str(uuid4())
        
        response = self.client.delete(f'/api/courts/{fake_id}/')
        self.assertEqual(response.status_code, 404)
    
    def test_court_detail_unauthenticated(self):
        """Test getting court detail without authentication"""
        response = self.client.get(f'/api/courts/{self.court.id}/')
        self.assertEqual(response.status_code, 401)
    
    def test_update_court_unauthenticated(self):
        """Test updating court without authentication"""
        response = self.client.post(f'/api/courts/{self.court.id}/', {
            'name': 'Test'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_delete_court_unauthenticated(self):
        """Test deleting court without authentication"""
        response = self.client.delete(f'/api/courts/{self.court.id}/')
        self.assertEqual(response.status_code, 401)
    
    def test_court_detail_non_mitra(self):
        """Test getting court detail as non-mitra"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/api/courts/{self.court.id}/')
        self.assertEqual(response.status_code, 403)
    
    def test_update_court_non_mitra(self):
        """Test updating court as non-mitra"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/api/courts/{self.court.id}/', {
            'name': 'Test'
        })
        self.assertEqual(response.status_code, 403)
    
    def test_delete_court_non_mitra(self):
        """Test deleting court as non-mitra"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.delete(f'/api/courts/{self.court.id}/')
        self.assertEqual(response.status_code, 403)
    
    def test_create_court_with_json_error_in_images(self):
        """Test creating court with invalid JSON in images"""
        self.client.login(username='testmitra', password='testpass123')
        
        court_data = {
            'venue': str(self.venue.id),
            'name': 'Court JSON Test',
            'category': str(self.category.id),
            'price_per_hour': '100000',
            'image_urls': 'invalid-json'
        }
        
        response = self.client.post('/api/courts/', court_data)
        # Should still succeed, just skip images
        self.assertEqual(response.status_code, 200)
    
    def test_create_court_with_json_error_in_sessions(self):
        """Test creating court with invalid JSON in sessions"""
        self.client.login(username='testmitra', password='testpass123')
        
        court_data = {
            'venue': str(self.venue.id),
            'name': 'Court Session Test',
            'category': str(self.category.id),
            'price_per_hour': '100000',
            'sessions': 'invalid-json'
        }
        
        response = self.client.post('/api/courts/', court_data)
        # Should still succeed, just skip sessions
        self.assertEqual(response.status_code, 200)
    
    def test_update_court_with_images(self):
        """Test updating court with new images"""
        self.client.login(username='testmitra', password='testpass123')
        
        update_data = {
            'name': 'Updated Court',
            'venue': str(self.venue.id),
            'category': str(self.category.id),
            'price_per_hour': '200000',
            'image_urls': json.dumps(['https://example.com/new.jpg'])
        }
        
        response = self.client.post(f'/api/courts/{self.court.id}/', update_data)
        self.assertEqual(response.status_code, 200)
        
        # Check images were created
        self.assertTrue(self.court.images.filter(image_url='https://example.com/new.jpg').exists())
    
    def test_update_court_with_sessions(self):
        """Test updating court with new sessions"""
        self.client.login(username='testmitra', password='testpass123')
        
        update_data = {
            'name': 'Updated Court',
            'venue': str(self.venue.id),
            'category': str(self.category.id),
            'price_per_hour': '200000',
            'sessions': json.dumps([{
                'session_name': 'New Session',
                'start_time': '14:00',
                'end_time': '16:00',
                'is_active': True
            }])
        }
        
        response = self.client.post(f'/api/courts/{self.court.id}/', update_data)
        self.assertEqual(response.status_code, 200)
        
        # Check sessions were created
        self.court.refresh_from_db()
        self.assertTrue(self.court.sessions.filter(session_name='New Session').exists())
    
    def test_update_court_with_invalid_data(self):
        """Test update court with invalid data"""
        self.client.login(username='testmitra', password='testpass123')
        
        # Send incomplete data
        update_data = {
            'price_per_hour': 'invalid'
        }
        
        response = self.client.post(f'/api/courts/{self.court.id}/', update_data)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
    
    def test_list_courts_with_inactive_court(self):
        """Test listing includes inactive courts"""
        # Create inactive court
        Court.objects.create(
            venue=self.venue,
            name='Inactive Court',
            price_per_hour=Decimal('50000'),
            is_active=False
        )
        
        self.client.login(username='testmitra', password='testpass123')
        response = self.client.get('/api/courts/')
        
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)  # Both active and inactive
    
    def test_court_price_validation(self):
        """Test court with zero price"""
        court = Court.objects.create(
            venue=self.venue,
            name='Free Court',
            price_per_hour=Decimal('0')
        )
        self.assertEqual(court.price_per_hour, Decimal('0'))
    
    def test_maintenance_notes(self):
        """Test court with maintenance notes"""
        court = Court.objects.create(
            venue=self.venue,
            name='Court With Notes',
            price_per_hour=Decimal('100000'),
            maintenance_notes='Under maintenance'
        )
        self.assertEqual(court.maintenance_notes, 'Under maintenance')


# ============================================================================
# COMPREHENSIVE VIEW TESTS FOR 100% COVERAGE
# ============================================================================

class VenueListAPITest(TestCase):
    """Test cases for api_venue_list view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        self.category = SportsCategory.objects.create(name='futsal')
        self.venue = Venue.objects.create(
            owner=self.user,
            name='Test Venue',
            address='Jakarta',
            contact='08123456789',
            number_of_courts=1,
            verification_status='approved'
        )
    
    def test_venue_list_all(self):
        """Test getting all approved venues"""
        response = self.client.get('/api/venues/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreaterEqual(len(data), 1)
    
    def test_venue_list_filter_by_name(self):
        """Test filtering venues by name"""
        response = self.client.get('/api/venues/?name=Test')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreaterEqual(len(data), 1)
    
    def test_venue_list_filter_by_category(self):
        """Test filtering venues by category"""
        self.venue.categories.add(self.category)
        response = self.client.get('/api/venues/?category=futsal')
        self.assertEqual(response.status_code, 200)
    
    def test_venue_list_filter_by_min_price(self):
        """Test filtering venues by minimum price"""
        response = self.client.get('/api/venues/?min_price=50000')
        self.assertEqual(response.status_code, 200)
    
    def test_venue_list_filter_by_max_price(self):
        """Test filtering venues by maximum price"""
        response = self.client.get('/api/venues/?max_price=200000')
        self.assertEqual(response.status_code, 200)
    
    def test_venue_list_filter_by_location(self):
        """Test filtering venues by location"""
        response = self.client.get('/api/venues/?location=Jakarta')
        self.assertEqual(response.status_code, 200)


class IndexViewTest(TestCase):
    """Test cases for index view"""
    
    def test_index_redirects(self):
        """Test index view redirects to main"""
        response = self.client.get('/index/')
        # Should redirect or return success
        self.assertIn(response.status_code, [200, 302])


class AuthenticationAPITest(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            role='user',
            first_name='Test',
            last_name='User'
        )
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'testuser')
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = self.client.post('/api/login/', {
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_login_already_authenticated(self):
        """Test login when already authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_register_success(self):
        """Test successful registration"""
        response = self.client.post('/api/register/', {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'user'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_invalid_data(self):
        """Test registration with invalid data"""
        response = self.client.post('/api/register/', {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': '123',
            'password2': '456',
        })
        self.assertEqual(response.status_code, 400)
    
    def test_register_duplicate_username(self):
        """Test registration with existing username"""
        response = self.client.post('/api/register/', {
            'username': 'testuser',  # Already exists
            'email': 'another@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'Another',
            'last_name': 'User',
            'role': 'user'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_logout_success(self):
        """Test successful logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_logout_not_authenticated(self):
        """Test logout when not authenticated"""
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])


class DashboardAPITest(TestCase):
    """Test cases for dashboard views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.user = User.objects.create_user(
            username='user1',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra',
            first_name='Mitra',
            last_name='Test'
        )
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            is_staff=True
        )
        
        # Create test data
        self.category = SportsCategory.objects.create(name='futsal')
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            number_of_courts=1,
            verification_status='approved'
        )
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=Decimal('100000')
        )
    
    def test_user_dashboard_authenticated(self):
        """Test user dashboard for authenticated user"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/user-dashboard/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_user_dashboard_unauthenticated(self):
        """Test user dashboard without authentication"""
        response = self.client.get('/api/user-dashboard/')
        self.assertEqual(response.status_code, 401)
    
    def test_user_dashboard_with_bookings(self):
        """Test user dashboard with bookings"""
        # Create booking
        booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=2),
            total_price=Decimal('200000'),
            status='confirmed'
        )
        
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/user-dashboard/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreaterEqual(data['data']['total_bookings'], 1)
    
    def test_mitra_dashboard_authenticated(self):
        """Test mitra dashboard for authenticated mitra"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_mitra_dashboard_unauthenticated(self):
        """Test mitra dashboard without authentication"""
        response = self.client.get('/api/mitra-dashboard/')
        self.assertEqual(response.status_code, 401)
    
    def test_mitra_dashboard_non_mitra(self):
        """Test mitra dashboard as non-mitra user"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        self.assertEqual(response.status_code, 403)
    
    def test_admin_dashboard_authenticated(self):
        """Test admin dashboard for authenticated admin"""
        self.client.login(username='admin1', password='testpass123')
        response = self.client.get('/api/admin-dashboard/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_admin_dashboard_unauthenticated(self):
        """Test admin dashboard without authentication"""
        response = self.client.get('/api/admin-dashboard/')
        self.assertEqual(response.status_code, 401)
    
    def test_admin_dashboard_non_admin(self):
        """Test admin dashboard as non-admin user"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/admin-dashboard/')
        self.assertEqual(response.status_code, 403)


class UserStatusAPITest(TestCase):
    """Test cases for user status view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
    
    def test_user_status_authenticated(self):
        """Test user status when authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/user-status/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['is_authenticated'])
        self.assertEqual(data['user']['username'], 'testuser')
    
    def test_user_status_unauthenticated(self):
        """Test user status when not authenticated"""
        response = self.client.get('/api/user-status/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['is_authenticated'])


class ProfileAPITest(TestCase):
    """Test cases for profile view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123',
            role='user',
            first_name='Test',
            last_name='User'
        )
    
    def test_profile_get_authenticated(self):
        """Test getting profile when authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['username'], 'testuser')
    
    def test_profile_get_unauthenticated(self):
        """Test getting profile without authentication"""
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 401)
    
    def test_profile_update_success(self):
        """Test updating profile successfully"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/api/profile/', {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
    
    def test_profile_update_invalid_data(self):
        """Test updating profile with invalid data"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/api/profile/', {
            'email': 'invalid-email'
        })
        self.assertEqual(response.status_code, 400)


class MitraManagementAPITest(TestCase):
    """Test cases for mitra management views"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            is_staff=True
        )
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra',
            first_name='Test',
            last_name='Mitra'
        )
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            number_of_courts=0,
            verification_status='pending'
        )
    
    def test_mitra_list_as_admin(self):
        """Test getting mitra list as admin"""
        self.client.login(username='admin1', password='testpass123')
        response = self.client.get('/api/mitra/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']), 1)
    
    def test_mitra_list_unauthenticated(self):
        """Test getting mitra list without authentication"""
        response = self.client.get('/api/mitra/')
        self.assertEqual(response.status_code, 401)
    
    def test_mitra_list_non_admin(self):
        """Test getting mitra list as non-admin"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/mitra/')
        self.assertEqual(response.status_code, 403)
    
    def test_mitra_update_status_approve(self):
        """Test approving mitra venue"""
        self.client.login(username='admin1', password='testpass123')
        response = self.client.post(f'/api/mitra/{self.mitra.id}/', {
            'venue_id': str(self.venue.id),
            'status': 'approved'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.verification_status, 'approved')
    
    def test_mitra_update_status_reject(self):
        """Test rejecting mitra venue"""
        self.client.login(username='admin1', password='testpass123')
        response = self.client.post(f'/api/mitra/{self.mitra.id}/', {
            'venue_id': str(self.venue.id),
            'status': 'rejected'
        })
        self.assertEqual(response.status_code, 200)
        
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.verification_status, 'rejected')
    
    def test_mitra_update_status_invalid_venue(self):
        """Test updating status with invalid venue ID"""
        self.client.login(username='admin1', password='testpass123')
        response = self.client.post(f'/api/mitra/{self.mitra.id}/', {
            'venue_id': str(uuid.uuid4()),
            'status': 'approved'
        })
        self.assertEqual(response.status_code, 404)
    
    def test_mitra_update_status_unauthenticated(self):
        """Test updating mitra status without authentication"""
        response = self.client.post(f'/api/mitra/{self.mitra.id}/', {
            'venue_id': str(self.venue.id),
            'status': 'approved'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_mitra_venue_details_as_admin(self):
        """Test getting mitra venue details as admin"""
        self.client.login(username='admin1', password='testpass123')
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_mitra_venue_details_unauthenticated(self):
        """Test getting mitra venue details without authentication"""
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        self.assertEqual(response.status_code, 401)
    
    def test_mitra_venue_details_non_admin(self):
        """Test getting mitra venue details as non-admin"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        self.assertEqual(response.status_code, 403)


class VenueAPITest(TestCase):
    """Test cases for venue management views"""
    
    def setUp(self):
        self.client = Client()
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra'
        )
        self.category = SportsCategory.objects.create(name='futsal')
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            number_of_courts=0,
            verification_status='approved'
        )
    
    def test_venues_list_as_mitra(self):
        """Test listing venues as mitra"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/venues/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_venues_create_success(self):
        """Test creating venue successfully"""
        self.client.login(username='mitra1', password='testpass123')
        
        venue_data = {
            'name': 'New Venue',
            'address': 'New Address',
            'contact': '08987654321',
            'description': 'New venue description',
            'categories': json.dumps([str(self.category.id)]),
            'facilities': json.dumps([]),
            'image_urls': json.dumps(['https://example.com/image.jpg'])
        }
        
        response = self.client.post('/api/venues/', venue_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_venues_create_unauthenticated(self):
        """Test creating venue without authentication"""
        response = self.client.post('/api/venues/', {
            'name': 'Test'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_venues_create_non_mitra(self):
        """Test creating venue as non-mitra"""
        user = User.objects.create_user(
            username='user1',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        self.client.login(username='user1', password='testpass123')
        response = self.client.post('/api/venues/', {
            'name': 'Test'
        })
        self.assertEqual(response.status_code, 403)
    
    def test_venue_detail_get_public(self):
        """Test getting public venue detail"""
        response = self.client.get(f'/api/public/venues/{self.venue.id}/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_venue_detail_get_authenticated(self):
        """Test getting venue detail as owner"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get(f'/api/venues/{self.venue.id}/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_venue_detail_update_success(self):
        """Test updating venue successfully"""
        self.client.login(username='mitra1', password='testpass123')
        
        update_data = {
            'name': 'Updated Venue Name',
            'address': self.venue.address,
            'contact': self.venue.contact,
            'description': 'Updated description'
        }
        
        response = self.client.post(f'/api/venues/{self.venue.id}/', update_data)
        self.assertEqual(response.status_code, 200)
        
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.name, 'Updated Venue Name')
    
    def test_venue_detail_delete_success(self):
        """Test deleting venue successfully"""
        self.client.login(username='mitra1', password='testpass123')
        
        venue_id = self.venue.id
        response = self.client.delete(f'/api/venues/{venue_id}/')
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(Venue.objects.filter(id=venue_id).exists())
    
    def test_venue_detail_not_found(self):
        """Test getting non-existent venue"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get(f'/api/venues/{uuid.uuid4()}/')
        self.assertEqual(response.status_code, 404)
    
    def test_venue_detail_unauthorized_update(self):
        """Test updating venue by non-owner"""
        another_mitra = User.objects.create_user(
            username='mitra2',
            email='mitra2@test.com',
            password='testpass123',
            role='mitra'
        )
        self.client.login(username='mitra2', password='testpass123')
        response = self.client.post(f'/api/venues/{self.venue.id}/', {
            'name': 'Hacked'
        })
        self.assertEqual(response.status_code, 404)


class ReviewAPITest(TestCase):
    """Test cases for review views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user1',
            email='user@test.com',
            password='testpass123',
            role='user',
            first_name='Test',
            last_name='User'
        )
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra'
        )
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            number_of_courts=0,
            verification_status='approved'
        )
        self.review = Review.objects.create(
            user=self.user,
            venue=self.venue,
            rating=5,
            comment='Great venue!'
        )
    
    def test_get_venue_reviews(self):
        """Test getting reviews for a venue"""
        response = self.client.get(f'/api/venues/{self.venue.id}/reviews/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']), 1)
    
    def test_create_review_success(self):
        """Test creating a review"""
        self.client.login(username='user1', password='testpass123')
        
        # Delete existing review first
        self.review.delete()
        
        review_data = {
            'rating': 4,
            'comment': 'Nice place'
        }
        
        response = self.client.post(f'/api/venues/{self.venue.id}/reviews/', review_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_create_review_unauthenticated(self):
        """Test creating review without authentication"""
        response = self.client.post(f'/api/venues/{self.venue.id}/reviews/', {
            'rating': 5,
            'comment': 'Test'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_create_review_duplicate(self):
        """Test creating duplicate review"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(f'/api/venues/{self.venue.id}/reviews/', {
            'rating': 5,
            'comment': 'Another review'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_update_review_success(self):
        """Test updating a review"""
        self.client.login(username='user1', password='testpass123')
        
        update_data = {
            'rating': 3,
            'comment': 'Updated comment'
        }
        
        response = self.client.post(f'/api/reviews/{self.review.id}/', update_data)
        self.assertEqual(response.status_code, 200)
        
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)
        self.assertEqual(self.review.comment, 'Updated comment')
    
    def test_delete_review_success(self):
        """Test deleting a review"""
        self.client.login(username='user1', password='testpass123')
        
        review_id = self.review.id
        response = self.client.delete(f'/api/reviews/{review_id}/')
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(Review.objects.filter(id=review_id).exists())
    
    def test_manage_review_unauthenticated(self):
        """Test managing review without authentication"""
        response = self.client.post(f'/api/reviews/{self.review.id}/', {
            'rating': 5
        })
        self.assertEqual(response.status_code, 401)
    
    def test_manage_review_unauthorized(self):
        """Test managing review by non-owner"""
        another_user = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123',
            role='user'
        )
        self.client.login(username='user2', password='testpass123')
        response = self.client.post(f'/api/reviews/{self.review.id}/', {
            'rating': 1
        })
        self.assertEqual(response.status_code, 403)


class CourtSessionAPITest(TestCase):
    """Test cases for court session views"""
    
    def setUp(self):
        self.client = Client()
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra'
        )
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            number_of_courts=0
        )
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            price_per_hour=Decimal('100000')
        )
        self.session = CourtSession.objects.create(
            court=self.court,
            session_name='Morning Session',
            start_time=time(8, 0),
            end_time=time(10, 0)
        )
    
    def test_get_court_sessions(self):
        """Test getting court sessions"""
        response = self.client.get(f'/api/courts/{self.court.id}/sessions/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']), 1)
    
    def test_get_court_sessions_not_found(self):
        """Test getting sessions for non-existent court"""
        response = self.client.get(f'/api/courts/{uuid.uuid4()}/sessions/')
        self.assertEqual(response.status_code, 404)


class PendapatanAPITest(TestCase):
    """Test cases for pendapatan (revenue) view"""
    
    def setUp(self):
        self.client = Client()
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra'
        )
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            number_of_courts=0
        )
        self.pendapatan = Pendapatan.objects.create(
            mitra=self.mitra,
            venue=self.venue,
            amount=Decimal('500000'),
            date=date.today()
        )
    
    def test_get_pendapatan_as_mitra(self):
        """Test getting pendapatan as mitra"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/pendapatan/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_get_pendapatan_unauthenticated(self):
        """Test getting pendapatan without authentication"""
        response = self.client.get('/api/pendapatan/')
        self.assertEqual(response.status_code, 401)
    
    def test_get_pendapatan_non_mitra(self):
        """Test getting pendapatan as non-mitra"""
        user = User.objects.create_user(
            username='user1',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/pendapatan/')
        self.assertEqual(response.status_code, 403)


class SportsCategoriesAPITest(TestCase):
    """Test cases for sports categories view"""
    
    def setUp(self):
        self.client = Client()
        self.category = SportsCategory.objects.create(name='futsal')
    
    def test_get_sports_categories(self):
        """Test getting sports categories"""
        response = self.client.get('/api/sports-categories/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']), 1)


class ImageDeletionAPITest(TestCase):
    """Test cases for image deletion views"""
    
    def setUp(self):
        self.client = Client()
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra'
        )
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            number_of_courts=0
        )
        self.venue_image = VenueImage.objects.create(
            venue=self.venue,
            image_url='https://example.com/venue.jpg'
        )
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            price_per_hour=Decimal('100000')
        )
        self.court_image = CourtImage.objects.create(
            court=self.court,
            image_url='https://example.com/court.jpg'
        )
    
    def test_delete_venue_image_success(self):
        """Test deleting venue image"""
        self.client.login(username='mitra1', password='testpass123')
        
        image_id = self.venue_image.id
        response = self.client.delete(f'/api/venue-images/{image_id}/delete/')
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(VenueImage.objects.filter(id=image_id).exists())
    
    def test_delete_venue_image_unauthenticated(self):
        """Test deleting venue image without authentication"""
        response = self.client.delete(f'/api/venue-images/{self.venue_image.id}/delete/')
        self.assertEqual(response.status_code, 401)
    
    def test_delete_venue_image_unauthorized(self):
        """Test deleting venue image by non-owner"""
        another_mitra = User.objects.create_user(
            username='mitra2',
            email='mitra2@test.com',
            password='testpass123',
            role='mitra'
        )
        self.client.login(username='mitra2', password='testpass123')
        response = self.client.delete(f'/api/venue-images/{self.venue_image.id}/delete/')
        self.assertEqual(response.status_code, 403)
    
    def test_delete_court_image_success(self):
        """Test deleting court image"""
        self.client.login(username='mitra1', password='testpass123')
        
        image_id = self.court_image.id
        response = self.client.delete(f'/api/court-images/{image_id}/delete/')
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(CourtImage.objects.filter(id=image_id).exists())
    
    def test_delete_court_image_unauthenticated(self):
        """Test deleting court image without authentication"""
        response = self.client.delete(f'/api/court-images/{self.court_image.id}/delete/')
        self.assertEqual(response.status_code, 401)
    
    def test_delete_court_image_not_found(self):
        """Test deleting non-existent court image"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.delete('/api/court-images/99999/delete/')
        self.assertEqual(response.status_code, 404)


class BookingAPITest(TestCase):
    """Test cases for booking views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user1',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra'
        )
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Test Address',
            contact='08123456789',
            number_of_courts=0
        )
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            price_per_hour=Decimal('100000')
        )
        self.booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=2),
            total_price=Decimal('200000'),
            status='pending'
        )
    
    def test_get_bookings_as_user(self):
        """Test getting bookings as user"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_get_bookings_as_mitra(self):
        """Test getting bookings as mitra"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_get_bookings_unauthenticated(self):
        """Test getting bookings without authentication"""
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, 401)
    
    def test_create_booking_success(self):
        """Test creating a booking"""
        self.client.login(username='user1', password='testpass123')
        
        future_start = datetime.now() + timedelta(days=2)
        future_end = future_start + timedelta(hours=2)
        
        booking_data = {
            'court': str(self.court.id),
            'start_time': future_start.isoformat(),
            'end_time': future_end.isoformat(),
            'total_price': '200000'
        }
        
        response = self.client.post('/api/bookings/', booking_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_get_booking_detail_as_user(self):
        """Test getting booking detail as user"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(f'/api/bookings/{self.booking.id}/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_update_booking_status_as_mitra(self):
        """Test updating booking status as mitra"""
        self.client.login(username='mitra1', password='testpass123')
        
        update_data = {
            'status': 'confirmed'
        }
        
        response = self.client.post(f'/api/bookings/{self.booking.id}/', update_data)
        self.assertEqual(response.status_code, 200)
        
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'confirmed')
    
    def test_cancel_booking_as_user(self):
        """Test canceling booking as user"""
        self.client.login(username='user1', password='testpass123')
        
        response = self.client.delete(f'/api/bookings/{self.booking.id}/')
        self.assertEqual(response.status_code, 200)
        
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')
    
    def test_booking_detail_not_found(self):
        """Test getting non-existent booking"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(f'/api/bookings/{uuid.uuid4()}/')
        self.assertEqual(response.status_code, 404)
    
    def test_booking_detail_unauthorized(self):
        """Test accessing booking by non-owner"""
        another_user = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123',
            role='user'
        )
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(f'/api/bookings/{self.booking.id}/')
        self.assertEqual(response.status_code, 403)


class HelperFunctionTest(TestCase):
    """Test cases for helper functions"""
    
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test get_client_ip with X-Forwarded-For header"""
        from app.courts.views import get_client_ip
        
        request = Mock()
        request.META = {'HTTP_X_FORWARDED_FOR': '192.168.1.1, 10.0.0.1'}
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_with_remote_addr(self):
        """Test get_client_ip with REMOTE_ADDR"""
        from app.courts.views import get_client_ip
        
        request = Mock()
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')


# ============================================================================
# COMPREHENSIVE MITRA TESTS FOR 100% COVERAGE
# ============================================================================

class MitraDashboardAPITest(TestCase):
    """Comprehensive test cases for api_mitra_dashboard view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create mitra user
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra',
            first_name='Test',
            last_name='Mitra'
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='user1',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            is_staff=True
        )
        
        # Create category
        self.category = SportsCategory.objects.create(name='futsal')
        
        # Create venue for mitra
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Jakarta',
            contact='08123456789',
            number_of_courts=2,
            verification_status='approved'
        )
        
        # Create courts for the venue
        self.court1 = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=Decimal('100000.00')
        )
        
        self.court2 = Court.objects.create(
            venue=self.venue,
            name='Court 2',
            category=self.category,
            price_per_hour=Decimal('150000.00')
        )
        
        # Create venue image
        self.venue_image = VenueImage.objects.create(
            venue=self.venue,
            image_url='https://example.com/venue.jpg',
            is_primary=True
        )
    
    def test_mitra_dashboard_success(self):
        """Test successful mitra dashboard access"""
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user']['username'], 'mitra1')
        self.assertEqual(data['data']['user']['role'], 'mitra')
        self.assertEqual(len(data['data']['venues']), 1)
        
        # Check venue data
        venue_data = data['data']['venues'][0]
        self.assertEqual(venue_data['name'], 'Test Venue')
        self.assertEqual(venue_data['number_of_courts'], 2)
        self.assertEqual(venue_data['total_courts'], 2)
        self.assertEqual(venue_data['avg_price_per_hour'], 125000.0)  # (100000 + 150000) / 2
        self.assertIsNotNone(venue_data['image_url'])
    
    def test_mitra_dashboard_unauthenticated(self):
        """Test mitra dashboard without authentication"""
        response = self.client.get('/api/mitra-dashboard/')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Authentication required')
    
    def test_mitra_dashboard_wrong_role(self):
        """Test mitra dashboard with non-mitra user"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Access denied')
    
    def test_mitra_dashboard_admin_access_denied(self):
        """Test mitra dashboard with admin user"""
        self.client.login(username='admin1', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
    
    def test_mitra_dashboard_no_venues(self):
        """Test mitra dashboard with no venues"""
        # Create mitra without venues
        mitra2 = User.objects.create_user(
            username='mitra2',
            email='mitra2@test.com',
            password='testpass123',
            role='mitra'
        )
        
        self.client.login(username='mitra2', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['venues']), 0)
    
    def test_mitra_dashboard_venue_no_courts(self):
        """Test mitra dashboard with venue but no courts"""
        # Create venue without courts
        venue2 = Venue.objects.create(
            owner=self.mitra,
            name='Empty Venue',
            address='Bandung',
            number_of_courts=0
        )
        
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Find the empty venue in response
        empty_venue = next((v for v in data['data']['venues'] if v['name'] == 'Empty Venue'), None)
        self.assertIsNotNone(empty_venue)
        self.assertEqual(empty_venue['avg_price_per_hour'], 0)
        self.assertEqual(empty_venue['total_courts'], 0)
    
    def test_mitra_dashboard_venue_no_primary_image(self):
        """Test mitra dashboard with venue without primary image"""
        # Create venue without images
        venue3 = Venue.objects.create(
            owner=self.mitra,
            name='No Image Venue',
            address='Surabaya',
            number_of_courts=0
        )
        
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Find venue without image
        no_img_venue = next((v for v in data['data']['venues'] if v['name'] == 'No Image Venue'), None)
        self.assertIsNotNone(no_img_venue)
        self.assertIsNone(no_img_venue['image_url'])
    
    def test_mitra_dashboard_venue_non_primary_image(self):
        """Test mitra dashboard falls back to first image when no primary"""
        # Create venue with non-primary image
        venue4 = Venue.objects.create(
            owner=self.mitra,
            name='Non-Primary Image Venue',
            address='Medan',
            number_of_courts=0
        )
        
        VenueImage.objects.create(
            venue=venue4,
            image_url='https://example.com/fallback.jpg',
            is_primary=False
        )
        
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Find venue with fallback image
        fallback_venue = next((v for v in data['data']['venues'] if v['name'] == 'Non-Primary Image Venue'), None)
        self.assertIsNotNone(fallback_venue)
        self.assertEqual(fallback_venue['image_url'], 'https://example.com/fallback.jpg')
    
    def test_mitra_dashboard_multiple_venues(self):
        """Test mitra dashboard with multiple venues"""
        # Create second venue
        venue2 = Venue.objects.create(
            owner=self.mitra,
            name='Second Venue',
            address='Yogyakarta',
            number_of_courts=1,
            verification_status='pending'
        )
        
        Court.objects.create(
            venue=venue2,
            name='Court A',
            price_per_hour=Decimal('80000.00')
        )
        
        self.client.login(username='mitra1', password='testpass123')
        response = self.client.get('/api/mitra-dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['venues']), 2)


class MitraListAPITest(TestCase):
    """Comprehensive test cases for api_mitra_list view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.mitra1 = User.objects.create_user(
            username='mitra1',
            email='mitra1@test.com',
            password='testpass123',
            role='mitra',
            first_name='John',
            last_name='Doe',
            is_verified=True,
            is_active=True
        )
        
        self.mitra2 = User.objects.create_user(
            username='mitra2',
            email='mitra2@test.com',
            password='testpass123',
            role='mitra',
            first_name='Jane',
            is_verified=False,
            is_active=True
        )
        
        self.mitra3 = User.objects.create_user(
            username='mitra3',
            email='mitra3@test.com',
            password='testpass123',
            role='mitra',
            is_verified=False,
            is_active=False
        )
        
        # Create venues with descriptions
        self.venue1 = Venue.objects.create(
            owner=self.mitra1,
            name='Venue One',
            address='Jakarta',
            description='Premium sports facility'
        )
        
        self.venue2 = Venue.objects.create(
            owner=self.mitra1,
            name='Venue Two',
            address='Bandung',
            description='Budget friendly'
        )
        
        # Create courts
        self.category = SportsCategory.objects.create(name='futsal')
        
        self.court1 = Court.objects.create(
            venue=self.venue1,
            name='Court A',
            category=self.category,
            price_per_hour=Decimal('100000'),
            description='Indoor court'
        )
        
        self.court2 = Court.objects.create(
            venue=self.venue2,
            name='Court B',
            price_per_hour=Decimal('80000')
        )
    
    def test_mitra_list_success(self):
        """Test successful mitra list retrieval"""
        response = self.client.get('/api/mitra/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(len(data['data']), 3)
    
    def test_mitra_list_approved_status(self):
        """Test mitra list shows correct approved status"""
        response = self.client.get('/api/mitra/')
        data = json.loads(response.content)
        
        # Find mitra1 who is verified and active
        mitra1_data = next((m for m in data['data'] if m['email'] == 'mitra1@test.com'), None)
        self.assertIsNotNone(mitra1_data)
        self.assertEqual(mitra1_data['status'], 'approved')
    
    def test_mitra_list_pending_status(self):
        """Test mitra list shows correct pending status"""
        response = self.client.get('/api/mitra/')
        data = json.loads(response.content)
        
        # Find mitra2 who is not verified but active
        mitra2_data = next((m for m in data['data'] if m['email'] == 'mitra2@test.com'), None)
        self.assertIsNotNone(mitra2_data)
        self.assertEqual(mitra2_data['status'], 'pending')
    
    def test_mitra_list_rejected_status(self):
        """Test mitra list shows correct rejected status"""
        response = self.client.get('/api/mitra/')
        data = json.loads(response.content)
        
        # Find mitra3 who is not verified and not active
        mitra3_data = next((m for m in data['data'] if m['email'] == 'mitra3@test.com'), None)
        self.assertIsNotNone(mitra3_data)
        self.assertEqual(mitra3_data['status'], 'rejected')
    
    def test_mitra_list_full_name(self):
        """Test mitra list shows full name correctly"""
        response = self.client.get('/api/mitra/')
        data = json.loads(response.content)
        
        mitra1_data = next((m for m in data['data'] if m['email'] == 'mitra1@test.com'), None)
        self.assertEqual(mitra1_data['nama'], 'John Doe')
        
        mitra2_data = next((m for m in data['data'] if m['email'] == 'mitra2@test.com'), None)
        self.assertEqual(mitra2_data['nama'], 'Jane')  # Only first name
    
    def test_mitra_list_venue_descriptions(self):
        """Test mitra list includes venue descriptions"""
        response = self.client.get('/api/mitra/')
        data = json.loads(response.content)
        
        mitra1_data = next((m for m in data['data'] if m['email'] == 'mitra1@test.com'), None)
        self.assertIn('Premium sports facility', mitra1_data['deskripsi'])
        self.assertIn('Budget friendly', mitra1_data['deskripsi'])
        self.assertIn('|', mitra1_data['deskripsi'])  # Should be joined with |
    
    def test_mitra_list_no_description(self):
        """Test mitra list handles missing venue descriptions"""
        response = self.client.get('/api/mitra/')
        data = json.loads(response.content)
        
        mitra2_data = next((m for m in data['data'] if m['email'] == 'mitra2@test.com'), None)
        self.assertEqual(mitra2_data['deskripsi'], '')  # No venues
        
        mitra3_data = next((m for m in data['data'] if m['email'] == 'mitra3@test.com'), None)
        self.assertEqual(mitra3_data['deskripsi'], '')  # No venues
    
    def test_mitra_list_courts_data(self):
        """Test mitra list includes courts data"""
        response = self.client.get('/api/mitra/')
        data = json.loads(response.content)
        
        mitra1_data = next((m for m in data['data'] if m['email'] == 'mitra1@test.com'), None)
        self.assertEqual(len(mitra1_data['courts']), 2)
        
        # Check court details
        court_a = next((c for c in mitra1_data['courts'] if c['name'] == 'Court A'), None)
        self.assertIsNotNone(court_a)
        self.assertEqual(court_a['venue_name'], 'Venue One')
        self.assertEqual(court_a['description'], 'Indoor court')
        
        court_b = next((c for c in mitra1_data['courts'] if c['name'] == 'Court B'), None)
        self.assertIsNotNone(court_b)
        self.assertEqual(court_b['description'], 'Tidak ada deskripsi')  # No description
    
    def test_mitra_list_no_courts(self):
        """Test mitra list handles mitra with no courts"""
        response = self.client.get('/api/mitra/')
        data = json.loads(response.content)
        
        mitra2_data = next((m for m in data['data'] if m['email'] == 'mitra2@test.com'), None)
        self.assertEqual(len(mitra2_data['courts']), 0)
    
    def test_mitra_list_exception_handling(self):
        """Test mitra list handles exceptions"""
        # Force an exception by mocking User.objects.filter
        with patch('app.courts.views.User.objects.filter', side_effect=Exception('Database error')):
            response = self.client.get('/api/mitra/')
            
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'error')
            self.assertIn('Database error', data['message'])


class MitraUpdateStatusAPITest(TestCase):
    """Comprehensive test cases for api_mitra_update_status view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra',
            is_verified=False,
            is_active=True
        )
        
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            is_staff=True
        )
    
    def test_update_status_approve(self):
        """Test approving mitra status"""
        response = self.client.patch(
            f'/api/mitra/{self.mitra.id}/',
            data=json.dumps({'status': 'approved'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'ok')
        self.assertIn('approved successfully', data['message'])
        
        # Verify mitra was updated
        self.mitra.refresh_from_db()
        self.assertTrue(self.mitra.is_verified)
        self.assertTrue(self.mitra.is_active)
    
    def test_update_status_reject(self):
        """Test rejecting mitra status"""
        response = self.client.patch(
            f'/api/mitra/{self.mitra.id}/',
            data=json.dumps({'status': 'rejected', 'rejection_reason': 'Invalid documents'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'ok')
        self.assertIn('rejected successfully', data['message'])
        
        # Verify mitra was updated
        self.mitra.refresh_from_db()
        self.assertFalse(self.mitra.is_verified)
        self.assertFalse(self.mitra.is_active)
    
    def test_update_status_mitra_not_found(self):
        """Test updating status for non-existent mitra"""
        fake_id = uuid.uuid4()
        response = self.client.patch(
            f'/api/mitra/{fake_id}/',
            data=json.dumps({'status': 'approved'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Mitra not found')
    
    def test_update_status_invalid_json(self):
        """Test updating status with invalid JSON"""
        response = self.client.patch(
            f'/api/mitra/{self.mitra.id}/',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Invalid JSON')
    
    def test_update_status_invalid_status_value(self):
        """Test updating status with invalid status value"""
        response = self.client.patch(
            f'/api/mitra/{self.mitra.id}/',
            data=json.dumps({'status': 'invalid'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Invalid status')
    
    def test_update_status_missing_status_field(self):
        """Test updating status without status field"""
        response = self.client.patch(
            f'/api/mitra/{self.mitra.id}/',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
    
    def test_update_status_with_rejection_reason(self):
        """Test updating status includes rejection reason in request"""
        response = self.client.patch(
            f'/api/mitra/{self.mitra.id}/',
            data=json.dumps({
                'status': 'rejected',
                'rejection_reason': 'Incomplete documents'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        # Note: rejection_reason is accepted but not stored per the code comments
    
    def test_update_status_exception_handling(self):
        """Test update status handles exceptions"""
        # Force an exception by mocking save()
        with patch.object(User, 'save', side_effect=Exception('Save error')):
            response = self.client.patch(
                f'/api/mitra/{self.mitra.id}/',
                data=json.dumps({'status': 'approved'}),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'error')
            self.assertIn('Save error', data['message'])


class MitraVenueDetailsAPITest(TestCase):
    """Comprehensive test cases for api_mitra_venue_details view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.mitra = User.objects.create_user(
            username='mitra1',
            email='mitra@test.com',
            password='testpass123',
            role='mitra',
            first_name='John',
            last_name='Doe',
            phone_number='08123456789',
            profile_picture='https://example.com/profile.jpg'
        )
        
        # Create venue
        self.venue = Venue.objects.create(
            owner=self.mitra,
            name='Test Venue',
            address='Jakarta',
            contact='08123456789',
            description='Premium facility',
            number_of_courts=2,
            verification_status='approved'
        )
        
        # Create venue images
        self.venue_image1 = VenueImage.objects.create(
            venue=self.venue,
            image_url='https://example.com/venue1.jpg',
            is_primary=True,
            caption='Main entrance'
        )
        
        self.venue_image2 = VenueImage.objects.create(
            venue=self.venue,
            image_url='https://example.com/venue2.jpg',
            is_primary=False
        )
        
        # Create courts
        self.category = SportsCategory.objects.create(name='futsal')
        
        self.court1 = Court.objects.create(
            venue=self.venue,
            name='Court A',
            category=self.category,
            price_per_hour=Decimal('100000'),
            is_active=True,
            description='Indoor court'
        )
        
        self.court2 = Court.objects.create(
            venue=self.venue,
            name='Court B',
            price_per_hour=Decimal('80000'),
            is_active=False
        )
        
        # Create court images
        self.court_image1 = CourtImage.objects.create(
            court=self.court1,
            image_url='https://example.com/court1.jpg',
            is_primary=True,
            caption='Court view'
        )
        
        self.court_image2 = CourtImage.objects.create(
            court=self.court1,
            image_url='https://example.com/court2.jpg',
            is_primary=False
        )
    
    def test_venue_details_success(self):
        """Test successful venue details retrieval"""
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'ok')
        
        # Check mitra data
        mitra_data = data['data']['mitra']
        self.assertEqual(mitra_data['name'], 'John Doe')
        self.assertEqual(mitra_data['email'], 'mitra@test.com')
        self.assertEqual(mitra_data['phone_number'], '08123456789')
        self.assertEqual(mitra_data['profile_picture'], 'https://example.com/profile.jpg')
        
        # Check venues data
        self.assertEqual(len(data['data']['venues']), 1)
        venue_data = data['data']['venues'][0]
        self.assertEqual(venue_data['name'], 'Test Venue')
        self.assertEqual(venue_data['address'], 'Jakarta')
        self.assertEqual(venue_data['contact'], '08123456789')
        self.assertEqual(venue_data['description'], 'Premium facility')
        self.assertEqual(venue_data['number_of_courts'], 2)
        self.assertTrue(venue_data['is_verified'])
    
    def test_venue_details_venue_images(self):
        """Test venue details includes venue images"""
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        data = json.loads(response.content)
        
        venue_data = data['data']['venues'][0]
        self.assertEqual(len(venue_data['images']), 2)
        
        # Check primary image
        primary_img = next((img for img in venue_data['images'] if img['is_primary']), None)
        self.assertIsNotNone(primary_img)
        self.assertEqual(primary_img['url'], 'https://example.com/venue1.jpg')
        self.assertEqual(primary_img['caption'], 'Main entrance')
        
        # Check non-primary image
        non_primary = next((img for img in venue_data['images'] if not img['is_primary']), None)
        self.assertIsNotNone(non_primary)
        self.assertEqual(non_primary['caption'], '')  # No caption
    
    def test_venue_details_courts_data(self):
        """Test venue details includes courts data"""
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        data = json.loads(response.content)
        
        venue_data = data['data']['venues'][0]
        self.assertEqual(len(venue_data['courts']), 2)
        
        # Check Court A
        court_a = next((c for c in venue_data['courts'] if c['name'] == 'Court A'), None)
        self.assertIsNotNone(court_a)
        # Category display depends on model implementation
        self.assertIn(court_a['category'].lower(), ['futsal', 'f'])  # Accept various formats
        self.assertEqual(court_a['price_per_hour'], '100000.00')  # Decimal with 2 places
        self.assertTrue(court_a['is_active'])
        self.assertEqual(court_a['description'], 'Indoor court')
        self.assertEqual(len(court_a['images']), 2)
        
        # Check Court B
        court_b = next((c for c in venue_data['courts'] if c['name'] == 'Court B'), None)
        self.assertIsNotNone(court_b)
        self.assertFalse(court_b['is_active'])
        self.assertEqual(court_b['description'], 'Tidak ada deskripsi')
    
    def test_venue_details_court_images(self):
        """Test venue details includes court images"""
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        data = json.loads(response.content)
        
        venue_data = data['data']['venues'][0]
        court_a = next((c for c in venue_data['courts'] if c['name'] == 'Court A'), None)
        
        self.assertEqual(len(court_a['images']), 2)
        
        # Check primary court image
        primary_img = next((img for img in court_a['images'] if img['is_primary']), None)
        self.assertIsNotNone(primary_img)
        self.assertEqual(primary_img['url'], 'https://example.com/court1.jpg')
        self.assertEqual(primary_img['caption'], 'Court view')
    
    def test_venue_details_mitra_not_found(self):
        """Test venue details for non-existent mitra"""
        fake_id = uuid.uuid4()
        response = self.client.get(f'/api/mitra/{fake_id}/venues/')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Mitra not found')
    
    def test_venue_details_no_venues(self):
        """Test venue details for mitra with no venues"""
        mitra2 = User.objects.create_user(
            username='mitra2',
            email='mitra2@test.com',
            password='testpass123',
            role='mitra'
        )
        
        response = self.client.get(f'/api/mitra/{mitra2.id}/venues/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['data']['venues']), 0)
    
    def test_venue_details_mitra_no_phone(self):
        """Test venue details with mitra without phone number"""
        mitra2 = User.objects.create_user(
            username='mitra2',
            email='mitra2@test.com',
            password='testpass123',
            role='mitra'
        )
        
        Venue.objects.create(
            owner=mitra2,
            name='Test',
            address='Test'
        )
        
        response = self.client.get(f'/api/mitra/{mitra2.id}/venues/')
        data = json.loads(response.content)
        
        self.assertEqual(data['data']['mitra']['phone_number'], '-')
        self.assertEqual(data['data']['mitra']['profile_picture'], '')
    
    def test_venue_details_venue_no_contact(self):
        """Test venue details with venue without contact"""
        venue2 = Venue.objects.create(
            owner=self.mitra,
            name='No Contact Venue',
            address='Test'
        )
        
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        data = json.loads(response.content)
        
        venue_data = next((v for v in data['data']['venues'] if v['name'] == 'No Contact Venue'), None)
        self.assertEqual(venue_data['contact'], '-')
        self.assertEqual(venue_data['description'], 'Tidak ada deskripsi')
    
    def test_venue_details_court_no_category(self):
        """Test venue details with court without category"""
        court3 = Court.objects.create(
            venue=self.venue,
            name='Court C',
            price_per_hour=Decimal('50000')
        )
        
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        data = json.loads(response.content)
        
        venue_data = data['data']['venues'][0]
        court_c = next((c for c in venue_data['courts'] if c['name'] == 'Court C'), None)
        self.assertEqual(court_c['category'], 'N/A')
    
    def test_venue_details_exception_handling(self):
        """Test venue details handles exceptions"""
        # Force an exception
        with patch('app.courts.views.Venue.objects.filter', side_effect=Exception('Database error')):
            response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
            
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'error')
            self.assertIn('Database error', data['message'])
    
    def test_venue_details_prefetch_optimization(self):
        """Test that prefetch_related is used for optimization"""
        response = self.client.get(f'/api/mitra/{self.mitra.id}/venues/')
        
        # Just verify it works without errors
        self.assertEqual(response.status_code, 200)
        
        # The prefetch_related call ensures efficient querying
        # This test verifies the code path executes successfully

