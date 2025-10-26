from django.test import TestCase
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal
from app.users.models import User
from app.venues.models import Venue, SportsCategory
from app.courts.models import Court, CourtSession
from app.bookings.models import Booking, Payment


class BookingModelTestCase(TestCase):
    """Test cases for Booking model"""
    
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
            number_of_courts=1,
            verification_status='approved'
        )
        
        self.court = Court.objects.create(
            venue=self.venue,
            name='Court 1',
            category=self.category,
            price_per_hour=100000
        )
        
        self.session = CourtSession.objects.create(
            court=self.court,
            session_name='Morning',
            start_time=time(8, 0),
            end_time=time(10, 0)
        )
    
    def test_booking_creation(self):
        """Test booking creation"""
        booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            session=self.session,
            booking_date=date.today(),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=2,
            total_price=200000
        )
        
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.court, self.court)
        self.assertEqual(booking.booking_status, 'pending')
        self.assertEqual(booking.payment_status, 'unpaid')
    
    def test_booking_str_representation(self):
        """Test booking string representation"""
        booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            booking_date=date.today(),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=2,
            total_price=200000
        )
        
        expected = f"testuser - Test Venue ({date.today()})"
        self.assertEqual(str(booking), expected)
    
    def test_booking_unique_together(self):
        """Test booking unique constraint"""
        Booking.objects.create(
            user=self.user,
            court=self.court,
            booking_date=date.today(),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=2,
            total_price=200000
        )
        
        # Trying to create duplicate booking should fail
        with self.assertRaises(Exception):
            Booking.objects.create(
                user=self.user,
                court=self.court,
                booking_date=date.today(),
                start_time=time(8, 0),
                end_time=time(10, 0),
                duration_hours=2,
                total_price=200000
            )


class PaymentModelTestCase(TestCase):
    """Test cases for Payment model"""
    
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
            total_price=200000
        )
    
    def test_payment_creation(self):
        """Test payment creation"""
        payment = Payment.objects.create(
            booking=self.booking,
            amount=200000,
            payment_method='bank_transfer'
        )
        
        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.amount, 200000)
        self.assertEqual(payment.payment_method, 'bank_transfer')
    
    def test_payment_str_representation(self):
        """Test payment string representation"""
        payment = Payment.objects.create(
            booking=self.booking,
            amount=200000,
            payment_method='bank_transfer'
        )
        
        expected = f"Payment for {self.booking}"
        self.assertEqual(str(payment), expected)

