from django.test import TestCase
from datetime import time
from app.users.models import User
from app.venues.models import Venue, SportsCategory, VenueImage, Facility, VenueFacility, OperationalHour


class SportsCategoryModelTestCase(TestCase):
    """Test cases for SportsCategory model"""
    
    def test_category_creation(self):
        """Test category creation"""
        category = SportsCategory.objects.create(
            name='FUTSAL',
            description='Futsal court'
        )
        
        self.assertEqual(category.name, 'FUTSAL')
        self.assertEqual(category.description, 'Futsal court')
    
    def test_category_str_representation(self):
        """Test category string representation"""
        category = SportsCategory.objects.create(
            name='FUTSAL'
        )
        
        # Should return the display value
        self.assertEqual(str(category), 'Futsal')


class VenueModelTestCase(TestCase):
    """Test cases for Venue model"""
    
    def setUp(self):
        """Set up test data"""
        self.mitra = User.objects.create_user(
            username='testmitra',
            password='testpass123',
            email='mitra@test.com',
            role='mitra'
        )
    
    def test_venue_creation(self):
        """Test venue creation"""
        venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            contact='081234567890',
            number_of_courts=2
        )
        
        self.assertEqual(venue.name, 'Test Venue')
        self.assertEqual(venue.owner, self.mitra)
        self.assertEqual(venue.verification_status, 'pending')
        self.assertEqual(venue.number_of_courts, 2)
    
    def test_venue_str_representation(self):
        """Test venue string representation"""
        venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            number_of_courts=1
        )
        
        self.assertEqual(str(venue), 'Test Venue')
    
    def test_venue_is_verified_property(self):
        """Test venue is_verified property"""
        venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            number_of_courts=1,
            verification_status='pending'
        )
        
        self.assertFalse(venue.is_verified)
        
        venue.verification_status = 'approved'
        venue.save()
        
        self.assertTrue(venue.is_verified)


class VenueImageModelTestCase(TestCase):
    """Test cases for VenueImage model"""
    
    def setUp(self):
        """Set up test data"""
        self.mitra = User.objects.create_user(
            username='testmitra',
            password='testpass123',
            email='mitra@test.com',
            role='mitra'
        )
        
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            number_of_courts=1
        )
    
    def test_venue_image_creation(self):
        """Test venue image creation"""
        image = VenueImage.objects.create(
            venue=self.venue,
            image_url='https://example.com/image.jpg',
            is_primary=True,
            caption='Main image'
        )
        
        self.assertEqual(image.venue, self.venue)
        self.assertTrue(image.is_primary)
        self.assertEqual(image.caption, 'Main image')
    
    def test_venue_image_str_representation(self):
        """Test venue image string representation"""
        image = VenueImage.objects.create(
            venue=self.venue,
            image_url='https://example.com/image.jpg'
        )
        
        expected = "Test Venue - Image"
        self.assertEqual(str(image), expected)


class FacilityModelTestCase(TestCase):
    """Test cases for Facility model"""
    
    def test_facility_creation(self):
        """Test facility creation"""
        facility = Facility.objects.create(
            name='Parking',
            description='Parking area'
        )
        
        self.assertEqual(facility.name, 'Parking')
        self.assertEqual(facility.description, 'Parking area')
    
    def test_facility_str_representation(self):
        """Test facility string representation"""
        facility = Facility.objects.create(
            name='Parking'
        )
        
        self.assertEqual(str(facility), 'Parking')


class VenueFacilityModelTestCase(TestCase):
    """Test cases for VenueFacility model"""
    
    def setUp(self):
        """Set up test data"""
        self.mitra = User.objects.create_user(
            username='testmitra',
            password='testpass123',
            email='mitra@test.com',
            role='mitra'
        )
        
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            number_of_courts=1
        )
        
        self.facility = Facility.objects.create(
            name='Parking'
        )
    
    def test_venue_facility_creation(self):
        """Test venue facility creation"""
        venue_facility = VenueFacility.objects.create(
            venue=self.venue,
            facility=self.facility
        )
        
        self.assertEqual(venue_facility.venue, self.venue)
        self.assertEqual(venue_facility.facility, self.facility)
    
    def test_venue_facility_str_representation(self):
        """Test venue facility string representation"""
        venue_facility = VenueFacility.objects.create(
            venue=self.venue,
            facility=self.facility
        )
        
        expected = "Test Venue - Parking"
        self.assertEqual(str(venue_facility), expected)
    
    def test_venue_facility_unique_together(self):
        """Test venue facility unique constraint"""
        VenueFacility.objects.create(
            venue=self.venue,
            facility=self.facility
        )
        
        # Trying to create duplicate should fail
        with self.assertRaises(Exception):
            VenueFacility.objects.create(
                venue=self.venue,
                facility=self.facility
            )


class OperationalHourModelTestCase(TestCase):
    """Test cases for OperationalHour model"""
    
    def setUp(self):
        """Set up test data"""
        self.mitra = User.objects.create_user(
            username='testmitra',
            password='testpass123',
            email='mitra@test.com',
            role='mitra'
        )
        
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            number_of_courts=1
        )
    
    def test_operational_hour_creation(self):
        """Test operational hour creation"""
        op_hour = OperationalHour.objects.create(
            venue=self.venue,
            day_of_week=0,  # Monday
            open_time=time(8, 0),
            close_time=time(22, 0)
        )
        
        self.assertEqual(op_hour.venue, self.venue)
        self.assertEqual(op_hour.day_of_week, 0)
        self.assertFalse(op_hour.is_closed)
    
    def test_operational_hour_str_representation(self):
        """Test operational hour string representation"""
        op_hour = OperationalHour.objects.create(
            venue=self.venue,
            day_of_week=0,  # Monday
            open_time=time(8, 0),
            close_time=time(22, 0)
        )
        
        expected = "Test Venue - Monday: 08:00:00-22:00:00"
        self.assertEqual(str(op_hour), expected)
    
    def test_operational_hour_unique_together(self):
        """Test operational hour unique constraint"""
        OperationalHour.objects.create(
            venue=self.venue,
            day_of_week=0,
            open_time=time(8, 0),
            close_time=time(22, 0)
        )
        
        # Trying to create duplicate should fail
        with self.assertRaises(Exception):
            OperationalHour.objects.create(
                venue=self.venue,
                day_of_week=0,
                open_time=time(9, 0),
                close_time=time(23, 0)
            )

