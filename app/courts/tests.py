from django.test import TestCase
from datetime import time
from app.users.models import User
from app.venues.models import Venue, SportsCategory
from app.courts.models import Court, CourtSession, CourtImage


class CourtModelTestCase(TestCase):
    """Test cases for Court model"""
    
    def setUp(self):
        """Set up test data"""
        self.mitra = User.objects.create_user(
            username='testmitra',
            password='testpass123',
            email='mitra@test.com',
            role='mitra'
        )
        
        self.category = SportsCategory.objects.create(
            name='FUTSAL',
            description='Futsal court'
        )
        
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            number_of_courts=1
        )
    
    def test_court_creation(self):
        """Test court creation"""
        court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=100000
        )
        
        self.assertEqual(court.venue, self.venue)
        self.assertEqual(court.name, 'Court 1')
        self.assertEqual(court.category, self.category)
        self.assertEqual(court.price_per_hour, 100000)
        self.assertTrue(court.is_active)
    
    def test_court_str_representation(self):
        """Test court string representation"""
        court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=100000
        )
        
        expected = f"Test Venue - Court 1 (Futsal)"
        self.assertEqual(str(court), expected)
    
    def test_court_unique_together(self):
        """Test court unique constraint"""
        Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=100000
        )
        
        # Trying to create duplicate court should fail
        with self.assertRaises(Exception):
            Court.objects.create(
                venue=self.venue,
                name='Court 1',
                category=self.category,
                price_per_hour=100000
            )


class CourtSessionModelTestCase(TestCase):
    """Test cases for CourtSession model"""
    
    def setUp(self):
        """Set up test data"""
        self.mitra = User.objects.create_user(
            username='testmitra',
            password='testpass123',
            email='mitra@test.com',
            role='mitra'
        )
        
        self.category = SportsCategory.objects.create(
            name='FUTSAL'
        )
        
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            number_of_courts=1
        )
        
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=100000
        )
    
    def test_session_creation(self):
        """Test session creation"""
        session = CourtSession.objects.create(
            court=self.court,
            session_name='Morning',
            start_time=time(8, 0),
            end_time=time(10, 0)
        )
        
        self.assertEqual(session.court, self.court)
        self.assertEqual(session.session_name, 'Morning')
        self.assertTrue(session.is_active)
    
    def test_session_str_representation(self):
        """Test session string representation"""
        session = CourtSession.objects.create(
            court=self.court,
            session_name='Morning',
            start_time=time(8, 0),
            end_time=time(10, 0)
        )
        
        expected = f"Court 1 - Morning (08:00:00-10:00:00)"
        self.assertEqual(str(session), expected)
    
    def test_session_unique_together(self):
        """Test session unique constraint"""
        CourtSession.objects.create(
            court=self.court,
            session_name='Morning',
            start_time=time(8, 0),
            end_time=time(10, 0)
        )
        
        # Trying to create duplicate session should fail
        with self.assertRaises(Exception):
            CourtSession.objects.create(
                court=self.court,
                session_name='Morning 2',
                start_time=time(8, 0),
                end_time=time(10, 0)
            )


class CourtImageModelTestCase(TestCase):
    """Test cases for CourtImage model"""
    
    def setUp(self):
        """Set up test data"""
        self.mitra = User.objects.create_user(
            username='testmitra',
            password='testpass123',
            email='mitra@test.com',
            role='mitra'
        )
        
        self.category = SportsCategory.objects.create(
            name='FUTSAL'
        )
        
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            number_of_courts=1
        )
        
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=100000
        )
    
    def test_court_image_creation(self):
        """Test court image creation"""
        image = CourtImage.objects.create(
            court=self.court,
            image_url='https://example.com/image.jpg',
            is_primary=True
        )
        
        self.assertEqual(image.court, self.court)
        self.assertEqual(image.image_url, 'https://example.com/image.jpg')
        self.assertTrue(image.is_primary)
    
    def test_court_image_str_representation(self):
        """Test court image string representation"""
        image = CourtImage.objects.create(
            court=self.court,
            image_url='https://example.com/image.jpg'
        )
        
        expected = "Test Venue - Court 1 - Image"
        self.assertEqual(str(image), expected)

