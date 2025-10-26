from django.test import TestCase
from datetime import date, time
from app.users.models import User
from app.venues.models import Venue, SportsCategory
from app.courts.models import Court
from app.bookings.models import Booking
from app.reviews.models import Review


class ReviewModelTestCase(TestCase):
    """Test cases for Review model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='user@test.com',
            role='user'
        )
        
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
        
        self.booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            booking_date=date.today(),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=2,
            total_price=200000,
            booking_status='completed'
        )
    
    def test_review_creation(self):
        """Test review creation"""
        review = Review.objects.create(
            booking=self.booking,
            rating=5,
            comment='Great venue!'
        )
        
        self.assertEqual(review.booking, self.booking)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great venue!')
    
    def test_review_str_representation(self):
        """Test review string representation"""
        review = Review.objects.create(
            booking=self.booking,
            rating=4,
            comment='Nice'
        )
        
        expected = "Review for Test Venue - 4 stars"
        self.assertEqual(str(review), expected)
    
    def test_review_rating_validation(self):
        """Test review rating validation"""
        # Rating should be between 1 and 5
        with self.assertRaises(Exception):
            Review.objects.create(
                booking=self.booking,
                rating=0,
                comment='Invalid'
            )
        
        # Create a new booking for second test
        booking2 = Booking.objects.create(
            user=self.user,
            court=self.court,
            booking_date=date.today(),
            start_time=time(10, 0),
            end_time=time(12, 0),
            duration_hours=2,
            total_price=200000,
            booking_status='completed'
        )
        
        with self.assertRaises(Exception):
            Review.objects.create(
                booking=booking2,
                rating=6,
                comment='Invalid'
            )

