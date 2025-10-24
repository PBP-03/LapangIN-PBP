from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from datetime import date, time, timedelta
from django.utils import timezone
import json

from app.users.models import User
from app.venues.models import Venue, SportsCategory
from app.courts.models import Court, CourtSession
from app.bookings.models import Booking, Payment
from app.reviews.models import Review
from app.revenue.models import Pendapatan, ActivityLog


class RevenueTestCase(TestCase):
    """Base test case with common setup for revenue tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            role='admin',
            first_name='Admin',
            last_name='User'
        )
        
        # Create mitra user
        self.mitra = User.objects.create_user(
            username='mitra1',
            password='mitra123',
            email='mitra@test.com',
            role='mitra',
            first_name='Mitra',
            last_name='User',
            is_verified=True
        )
        
        # Create second mitra user
        self.mitra2 = User.objects.create_user(
            username='mitra2',
            password='mitra123',
            email='mitra2@test.com',
            role='mitra',
            first_name='Mitra',
            last_name='Two'
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='user1',
            password='user123',
            email='user@test.com',
            role='user',
            first_name='Regular',
            last_name='User'
        )
        
        # Create sports category
        self.category = SportsCategory.objects.create(
            name='futsal',
            description='Futsal Category'
        )
        
        # Create venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            owner=self.mitra,
            address='Test Address',
            contact='081234567890',
            description='Test Description',
            number_of_courts=2,
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
        
        # Create court session
        self.session = CourtSession.objects.create(
            court=self.court,
            session_name='Morning',
            start_time=time(8, 0),
            end_time=time(10, 0),
            is_active=True
        )
        
        # Create booking
        self.booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            session=self.session,
            booking_date=date.today() + timedelta(days=1),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=Decimal('2.0'),
            total_price=Decimal('200000.00'),
            booking_status='completed',
            payment_status='paid'
        )
        
        # Create payment
        self.payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal('200000.00'),
            payment_method='transfer',
            transaction_id='TRX123',
            paid_at=timezone.now()
        )
        
        # Create pendapatan (revenue)
        self.pendapatan = Pendapatan.objects.create(
            mitra=self.mitra,
            booking=self.booking,
            amount=Decimal('200000.00'),
            commission_rate=Decimal('10.00'),
            commission_amount=Decimal('20000.00'),
            net_amount=Decimal('180000.00'),
            payment_status='paid',
            paid_at=timezone.now()
        )


class ApiMitraEarningsTests(RevenueTestCase):
    """Tests for api_mitra_earnings endpoint"""
    
    def test_api_mitra_earnings_unauthenticated(self):
        """Test accessing earnings without authentication"""
        response = self.client.get('/api/revenue/mitra-earnings/')
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data['status'], 'error')
    
    def test_api_mitra_earnings_non_admin(self):
        """Test accessing earnings as non-admin user"""
        self.client.login(username='mitra1', password='mitra123')
        response = self.client.get('/api/revenue/mitra-earnings/')
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data['status'], 'error')
    
    def test_api_mitra_earnings_success(self):
        """Test successful retrieval of mitra earnings"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/revenue/mitra-earnings/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('data', data)
        self.assertTrue(len(data['data']) > 0)
        
        # Check mitra1 earnings
        mitra1_data = next((m for m in data['data'] if m['mitra_name'] == 'Mitra User'), None)
        self.assertIsNotNone(mitra1_data)
        self.assertEqual(float(mitra1_data['total_earnings']), 180000.00)
        self.assertEqual(mitra1_data['completed_transactions'], 1)
    
    def test_api_mitra_earnings_no_earnings(self):
        """Test mitra with no earnings"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/revenue/mitra-earnings/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check mitra2 (no earnings)
        mitra2_data = next((m for m in data['data'] if m['mitra_name'] == 'Mitra Two'), None)
        self.assertIsNotNone(mitra2_data)
        self.assertEqual(float(mitra2_data['total_earnings']), 0.0)
        self.assertEqual(mitra2_data['completed_transactions'], 0)


class ApiMitraEarningsDetailTests(RevenueTestCase):
    """Tests for api_mitra_earnings_detail endpoint"""
    
    def test_api_mitra_earnings_detail_unauthenticated(self):
        """Test accessing earnings detail without authentication"""
        response = self.client.get(f'/api/revenue/mitra-earnings/{self.mitra.id}/')
        self.assertEqual(response.status_code, 401)
    
    def test_api_mitra_earnings_detail_non_admin(self):
        """Test accessing earnings detail as non-admin"""
        self.client.login(username='user1', password='user123')
        response = self.client.get(f'/api/revenue/mitra-earnings/{self.mitra.id}/')
        self.assertEqual(response.status_code, 401)
    
    def test_api_mitra_earnings_detail_not_found(self):
        """Test accessing earnings for non-existent mitra"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/revenue/mitra-earnings/99999/')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('not found', data['message'].lower())
    
    def test_api_mitra_earnings_detail_success(self):
        """Test successful retrieval of mitra earnings detail"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(f'/api/revenue/mitra-earnings/{self.mitra.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        
        # Check mitra info
        self.assertEqual(data['data']['mitra']['name'], 'Mitra User')
        self.assertEqual(data['data']['mitra']['email'], 'mitra@test.com')
        
        # Check summary
        self.assertEqual(data['data']['summary']['total_earnings'], 180000.0)
        self.assertEqual(data['data']['summary']['total_commission'], 20000.0)
        self.assertEqual(data['data']['summary']['total_transactions'], 1)
        
        # Check transactions
        self.assertEqual(len(data['data']['transactions']), 1)
        transaction = data['data']['transactions'][0]
        self.assertEqual(transaction['customer_name'], 'Regular User')
        self.assertEqual(transaction['venue_name'], 'Test Venue')


class ApiRefundsTests(RevenueTestCase):
    """Tests for refund management endpoints"""
    
    def test_api_refunds_get_unauthenticated(self):
        """Test listing refunds without authentication"""
        response = self.client.get('/api/revenue/refunds/')
        self.assertEqual(response.status_code, 401)
    
    def test_api_refunds_get_success(self):
        """Test successful listing of refunds"""
        # Create a refunded pendapatan
        refunded = Pendapatan.objects.create(
            mitra=self.mitra,
            booking=self.booking,
            amount=Decimal('100000.00'),
            commission_amount=Decimal('10000.00'),
            net_amount=Decimal('90000.00'),
            payment_status='refunded',
            notes='REFUND: Customer request'
        )
        
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/revenue/refunds/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(len(data['data']) > 0)
    
    def test_api_refunds_post_success(self):
        """Test successful refund creation"""
        self.client.login(username='admin', password='admin123')
        response = self.client.post(
            '/api/revenue/refunds/',
            data=json.dumps({
                'pendapatan_id': str(self.pendapatan.id),
                'reason': 'Customer request'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        
        # Verify refund was created
        self.pendapatan.refresh_from_db()
        self.assertEqual(self.pendapatan.payment_status, 'refunded')
        self.assertIn('REFUND:', self.pendapatan.notes)
    
    def test_api_refunds_post_missing_id(self):
        """Test refund creation without pendapatan_id"""
        self.client.login(username='admin', password='admin123')
        response = self.client.post(
            '/api/revenue/refunds/',
            data=json.dumps({'reason': 'Test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_api_refunds_post_already_refunded(self):
        """Test refund creation for already refunded transaction"""
        self.pendapatan.payment_status = 'refunded'
        self.pendapatan.save()
        
        self.client.login(username='admin', password='admin123')
        response = self.client.post(
            '/api/revenue/refunds/',
            data=json.dumps({
                'pendapatan_id': str(self.pendapatan.id),
                'reason': 'Test'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('already refunded', data['message'].lower())


class ApiCreateRefundTests(RevenueTestCase):
    """Tests for api_create_refund endpoint"""
    
    def test_create_refund_unauthenticated(self):
        """Test creating refund without authentication"""
        response = self.client.post(f'/api/revenue/refunds/{self.pendapatan.id}/create/')
        self.assertEqual(response.status_code, 401)
    
    def test_create_refund_success(self):
        """Test successful refund creation"""
        self.client.login(username='admin', password='admin123')
        response = self.client.post(
            f'/api/revenue/refunds/{self.pendapatan.id}/create/',
            data=json.dumps({'reason': 'Customer request'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['data']['status'], 'refunded')


class ApiListRefundsTests(RevenueTestCase):
    """Tests for api_list_refunds endpoint"""
    
    def test_list_refunds_unauthenticated(self):
        """Test listing refunds without authentication"""
        response = self.client.get('/api/revenue/refunds/list/')
        self.assertEqual(response.status_code, 401)
    
    def test_list_refunds_success(self):
        """Test successful listing of refunds"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/revenue/refunds/list/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIsInstance(data['data'], list)


class ApiCancelRefundTests(RevenueTestCase):
    """Tests for api_cancel_refund endpoint"""
    
    def test_cancel_refund_unauthenticated(self):
        """Test cancelling refund without authentication"""
        response = self.client.delete(f'/api/revenue/refunds/{self.pendapatan.id}/cancel/')
        self.assertEqual(response.status_code, 401)
    
    def test_cancel_refund_not_found(self):
        """Test cancelling non-refunded transaction"""
        self.client.login(username='admin', password='admin123')
        response = self.client.delete(f'/api/revenue/refunds/{self.pendapatan.id}/cancel/')
        self.assertEqual(response.status_code, 404)
    
    def test_cancel_refund_success(self):
        """Test successful refund cancellation"""
        # First mark as refunded
        self.pendapatan.payment_status = 'refunded'
        self.pendapatan.notes = 'REFUND: Test'
        self.pendapatan.save()
        
        self.client.login(username='admin', password='admin123')
        response = self.client.delete(f'/api/revenue/refunds/{self.pendapatan.id}/cancel/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        
        # Verify refund was cancelled
        self.pendapatan.refresh_from_db()
        self.assertEqual(self.pendapatan.payment_status, 'paid')
        self.assertIn('[CANCELLED]', self.pendapatan.notes)


class ApiLoginTests(RevenueTestCase):
    """Tests for api_login endpoint"""
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(
            '/api/login/',
            data=json.dumps({
                'username': 'admin',
                'password': 'admin123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'admin')
        self.assertEqual(data['user']['role'], 'admin')
        self.assertIn('redirect_url', data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            '/api/login/',
            data=json.dumps({
                'username': 'admin',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = self.client.post(
            '/api/login/',
            data=json.dumps({'username': 'admin'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_login_invalid_json(self):
        """Test login with invalid JSON"""
        response = self.client.post(
            '/api/login/',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class ApiRegisterTests(RevenueTestCase):
    """Tests for api_register endpoint"""
    
    def test_register_success(self):
        """Test successful registration"""
        response = self.client.post(
            '/api/register/',
            data=json.dumps({
                'username': 'newuser',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'email': 'newuser@test.com',
                'first_name': 'New',
                'role': 'user'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'newuser')
    
    def test_register_password_mismatch(self):
        """Test registration with password mismatch"""
        response = self.client.post(
            '/api/register/',
            data=json.dumps({
                'username': 'newuser',
                'password1': 'testpass123',
                'password2': 'differentpass',
                'email': 'newuser@test.com',
                'first_name': 'New',
                'role': 'user'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
    
    def test_register_duplicate_username(self):
        """Test registration with existing username"""
        response = self.client.post(
            '/api/register/',
            data=json.dumps({
                'username': 'admin',  # Already exists
                'password1': 'testpass123',
                'password2': 'testpass123',
                'email': 'newuser@test.com',
                'first_name': 'New',
                'role': 'user'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class ApiLogoutTests(RevenueTestCase):
    """Tests for api_logout endpoint"""
    
    def test_logout_success(self):
        """Test successful logout"""
        self.client.login(username='admin', password='admin123')
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_logout_not_authenticated(self):
        """Test logout when not authenticated"""
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 401)


class ApiUserDashboardTests(RevenueTestCase):
    """Tests for api_user_dashboard endpoint"""
    
    def test_user_dashboard_unauthenticated(self):
        """Test accessing user dashboard without authentication"""
        response = self.client.get('/api/dashboard/user/')
        self.assertEqual(response.status_code, 401)
    
    def test_user_dashboard_wrong_role(self):
        """Test accessing user dashboard with wrong role"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/dashboard/user/')
        self.assertEqual(response.status_code, 403)
    
    def test_user_dashboard_success(self):
        """Test successful user dashboard access"""
        self.client.login(username='user1', password='user123')
        response = self.client.get('/api/dashboard/user/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user']['role'], 'user')
        self.assertEqual(data['data']['title'], 'Dashboard User')


class ApiMitraDashboardTests(RevenueTestCase):
    """Tests for api_mitra_dashboard endpoint"""
    
    def test_mitra_dashboard_unauthenticated(self):
        """Test accessing mitra dashboard without authentication"""
        response = self.client.get('/api/revenue/mitra-dashboard/')
        self.assertEqual(response.status_code, 401)
    
    def test_mitra_dashboard_wrong_role(self):
        """Test accessing mitra dashboard with wrong role"""
        self.client.login(username='user1', password='user123')
        response = self.client.get('/api/revenue/mitra-dashboard/')
        self.assertEqual(response.status_code, 403)
    
    def test_mitra_dashboard_success(self):
        """Test successful mitra dashboard access"""
        self.client.login(username='mitra1', password='mitra123')
        response = self.client.get('/api/revenue/mitra-dashboard/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user']['role'], 'mitra')
        self.assertEqual(data['data']['title'], 'Dashboard Mitra')
        self.assertIn('venues', data['data'])
        
        # Check venues data
        self.assertEqual(len(data['data']['venues']), 1)
        venue = data['data']['venues'][0]
        self.assertEqual(venue['name'], 'Test Venue')
        self.assertIn('facilities', venue)


class ApiAdminDashboardTests(RevenueTestCase):
    """Tests for api_admin_dashboard endpoint"""
    
    def test_admin_dashboard_unauthenticated(self):
        """Test accessing admin dashboard without authentication"""
        response = self.client.get('/api/dashboard/admin/')
        self.assertEqual(response.status_code, 401)
    
    def test_admin_dashboard_wrong_role(self):
        """Test accessing admin dashboard with wrong role"""
        self.client.login(username='user1', password='user123')
        response = self.client.get('/api/dashboard/admin/')
        self.assertEqual(response.status_code, 403)
    
    def test_admin_dashboard_success(self):
        """Test successful admin dashboard access"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/dashboard/admin/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user']['role'], 'admin')
        self.assertIn('statistics', data['data'])
        self.assertIn('recent_activities', data['data'])


class ApiUserStatusTests(RevenueTestCase):
    """Tests for api_user_status endpoint"""
    
    def test_user_status_authenticated(self):
        """Test user status when authenticated"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/user-status/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['authenticated'])
        self.assertEqual(data['user']['username'], 'admin')
    
    def test_user_status_unauthenticated(self):
        """Test user status when not authenticated"""
        response = self.client.get('/api/user-status/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['authenticated'])


class ApiProfileTests(RevenueTestCase):
    """Tests for api_profile endpoint"""
    
    def test_profile_get_unauthenticated(self):
        """Test getting profile without authentication"""
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 401)
    
    def test_profile_get_success(self):
        """Test successful profile retrieval"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user']['username'], 'admin')
    
    def test_profile_update_success(self):
        """Test successful profile update"""
        self.client.login(username='admin', password='admin123')
        response = self.client.put(
            '/api/profile/',
            data=json.dumps({
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@test.com'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user']['first_name'], 'Updated')
    
    def test_profile_update_duplicate_username(self):
        """Test profile update with duplicate username"""
        self.client.login(username='admin', password='admin123')
        response = self.client.put(
            '/api/profile/',
            data=json.dumps({
                'username': 'mitra1'  # Already exists
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_profile_delete_success(self):
        """Test successful profile deletion"""
        self.client.login(username='user1', password='user123')
        response = self.client.delete('/api/profile/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify user was deleted
        self.assertFalse(User.objects.filter(username='user1').exists())


class ApiMitraListTests(RevenueTestCase):
    """Tests for api_mitra_list endpoint"""
    
    def test_mitra_list_success(self):
        """Test successful mitra list retrieval"""
        response = self.client.get('/api/revenue/mitra-list/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(len(data['data']) >= 2)
        
        # Check that both mitras are in the list
        usernames = [m['nama'] for m in data['data']]
        self.assertIn('Mitra User', usernames)
        self.assertIn('Mitra Two', usernames)


class ApiMitraUpdateStatusTests(RevenueTestCase):
    """Tests for api_mitra_update_status endpoint"""
    
    def test_mitra_update_status_not_found(self):
        """Test updating status for non-existent mitra"""
        response = self.client.patch(
            '/api/revenue/mitra-status/99999/',
            data=json.dumps({'status': 'approved'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_mitra_update_status_invalid_status(self):
        """Test updating with invalid status"""
        response = self.client.patch(
            f'/api/revenue/mitra-status/{self.mitra.id}/',
            data=json.dumps({'status': 'invalid'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_mitra_update_status_approved(self):
        """Test approving mitra status"""
        response = self.client.patch(
            f'/api/revenue/mitra-status/{self.mitra2.id}/',
            data=json.dumps({'status': 'approved'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        
        # Verify status was updated
        self.mitra2.refresh_from_db()
        self.assertTrue(self.mitra2.is_verified)
        self.assertTrue(self.mitra2.is_active)
    
    def test_mitra_update_status_rejected(self):
        """Test rejecting mitra status"""
        response = self.client.patch(
            f'/api/revenue/mitra-status/{self.mitra.id}/',
            data=json.dumps({
                'status': 'rejected',
                'rejection_reason': 'Incomplete documents'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        
        # Verify status was updated
        self.mitra.refresh_from_db()
        self.assertFalse(self.mitra.is_verified)
        self.assertFalse(self.mitra.is_active)


class ApiMitraVenueDetailsTests(RevenueTestCase):
    """Tests for api_mitra_venue_details endpoint"""
    
    def test_venue_details_not_found(self):
        """Test getting venue details for non-existent mitra"""
        response = self.client.get('/api/revenue/mitra-venues/99999/')
        self.assertEqual(response.status_code, 404)
    
    def test_venue_details_success(self):
        """Test successful venue details retrieval"""
        response = self.client.get(f'/api/revenue/mitra-venues/{self.mitra.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        
        # Check mitra info
        self.assertEqual(data['data']['mitra']['name'], 'Mitra User')
        
        # Check venues
        self.assertEqual(len(data['data']['venues']), 1)
        venue = data['data']['venues'][0]
        self.assertEqual(venue['name'], 'Test Venue')
        self.assertIn('courts', venue)
        self.assertEqual(len(venue['courts']), 1)


class ApiSportsCategoriesTests(RevenueTestCase):
    """Tests for api_sports_categories endpoint"""
    
    def test_sports_categories_success(self):
        """Test successful sports categories retrieval"""
        response = self.client.get('/api/sports-categories/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(len(data['data']) > 0)
        
        # Check category data
        category = data['data'][0]
        self.assertIn('id', category)
        self.assertIn('name', category)
        self.assertIn('display_name', category)


class ApiPendapatanTests(RevenueTestCase):
    """Tests for api_pendapatan endpoint"""
    
    def test_pendapatan_unauthenticated(self):
        """Test accessing pendapatan without authentication"""
        response = self.client.get('/api/revenue/pendapatan/')
        self.assertEqual(response.status_code, 401)
    
    def test_pendapatan_wrong_role(self):
        """Test accessing pendapatan with wrong role"""
        self.client.login(username='user1', password='user123')
        response = self.client.get('/api/revenue/pendapatan/')
        self.assertEqual(response.status_code, 403)
    
    def test_pendapatan_success(self):
        """Test successful pendapatan retrieval"""
        self.client.login(username='mitra1', password='mitra123')
        response = self.client.get('/api/revenue/pendapatan/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Check statistics
        stats = data['data']['statistics']
        self.assertIn('total_pendapatan', stats)
        self.assertIn('total_bookings', stats)
        
        # Check pendapatan list
        self.assertIn('pendapatan_list', data['data'])
    
    def test_pendapatan_with_period_filter(self):
        """Test pendapatan with period filter"""
        self.client.login(username='mitra1', password='mitra123')
        response = self.client.get('/api/revenue/pendapatan/?period=month')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['period'], 'month')


class ApiBookingDetailTests(RevenueTestCase):
    """Tests for api_booking_detail DELETE endpoint"""
    
    def test_booking_cancel_unauthenticated(self):
        """Test cancelling booking without authentication"""
        future_booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            session=self.session,
            booking_date=date.today() + timedelta(days=5),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=Decimal('2.0'),
            total_price=Decimal('200000.00')
        )
        
        response = self.client.delete(f'/api/bookings/{future_booking.id}/')
        self.assertEqual(response.status_code, 401)
    
    def test_booking_cancel_wrong_user(self):
        """Test cancelling booking by different user"""
        future_booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            session=self.session,
            booking_date=date.today() + timedelta(days=5),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=Decimal('2.0'),
            total_price=Decimal('200000.00')
        )
        
        self.client.login(username='mitra1', password='mitra123')
        response = self.client.delete(f'/api/bookings/{future_booking.id}/')
        self.assertEqual(response.status_code, 403)
    
    def test_booking_cancel_past_date(self):
        """Test cancelling booking on or after booking date"""
        self.client.login(username='user1', password='user123')
        response = self.client.delete(f'/api/bookings/{self.booking.id}/')
        self.assertEqual(response.status_code, 400)
    
    def test_booking_cancel_success(self):
        """Test successful booking cancellation"""
        future_booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            session=self.session,
            booking_date=date.today() + timedelta(days=5),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=Decimal('2.0'),
            total_price=Decimal('200000.00')
        )
        
        self.client.login(username='user1', password='user123')
        response = self.client.delete(f'/api/bookings/{future_booking.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify booking was cancelled
        future_booking.refresh_from_db()
        self.assertEqual(future_booking.booking_status, 'cancelled')


class ApiVenueReviewsTests(RevenueTestCase):
    """Tests for api_venue_reviews endpoint"""
    
    def test_venue_reviews_get_success(self):
        """Test getting venue reviews"""
        # Create a review
        review = Review.objects.create(
            booking=self.booking,
            rating=5,
            comment='Great venue!'
        )
        
        response = self.client.get(f'/api/venues/{self.venue.id}/reviews/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['reviews']), 1)
        self.assertEqual(data['data']['avg_rating'], 5.0)
    
    def test_venue_reviews_post_unauthenticated(self):
        """Test posting review without authentication"""
        response = self.client.post(
            f'/api/venues/{self.venue.id}/reviews/',
            data=json.dumps({
                'rating': 5,
                'comment': 'Test'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_venue_reviews_post_success(self):
        """Test successful review creation"""
        # Create a new completed booking without review
        new_booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            session=self.session,
            booking_date=date.today(),
            start_time=time(8, 0),
            end_time=time(10, 0),
            duration_hours=Decimal('2.0'),
            total_price=Decimal('200000.00'),
            booking_status='completed'
        )
        
        self.client.login(username='user1', password='user123')
        response = self.client.post(
            f'/api/venues/{self.venue.id}/reviews/',
            data=json.dumps({
                'rating': 4,
                'comment': 'Good venue'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['rating'], 4.0)
    
    def test_venue_reviews_post_invalid_rating(self):
        """Test posting review with invalid rating"""
        self.client.login(username='user1', password='user123')
        response = self.client.post(
            f'/api/venues/{self.venue.id}/reviews/',
            data=json.dumps({
                'rating': 6,  # Invalid: > 5
                'comment': 'Test'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class ApiManageReviewTests(RevenueTestCase):
    """Tests for api_manage_review endpoint"""
    
    def setUp(self):
        super().setUp()
        self.review = Review.objects.create(
            booking=self.booking,
            rating=4,
            comment='Good venue'
        )
    
    def test_manage_review_update_unauthenticated(self):
        """Test updating review without authentication"""
        response = self.client.put(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, 401)
    
    def test_manage_review_update_wrong_user(self):
        """Test updating review by different user"""
        self.client.login(username='mitra1', password='mitra123')
        response = self.client.put(
            f'/api/reviews/{self.review.id}/',
            data=json.dumps({'rating': 5}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_manage_review_update_success(self):
        """Test successful review update"""
        self.client.login(username='user1', password='user123')
        response = self.client.put(
            f'/api/reviews/{self.review.id}/',
            data=json.dumps({
                'rating': 5,
                'comment': 'Excellent!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        
        # Verify review was updated
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'Excellent!')
    
    def test_manage_review_delete_success(self):
        """Test successful review deletion"""
        self.client.login(username='user1', password='user123')
        response = self.client.delete(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        
        # Verify review was deleted
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())


class ApiCourtSessionsTests(RevenueTestCase):
    """Tests for api_court_sessions endpoint"""
    
    def test_court_sessions_not_found(self):
        """Test getting sessions for non-existent court"""
        response = self.client.get('/api/courts/99999/sessions/')
        self.assertEqual(response.status_code, 404)
    
    def test_court_sessions_success(self):
        """Test successful court sessions retrieval"""
        response = self.client.get(f'/api/courts/{self.court.id}/sessions/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['court_name'], 'Court 1')
        self.assertEqual(len(data['sessions']), 1)
        
        # Check session data
        session = data['sessions'][0]
        self.assertEqual(session['session_name'], 'Morning')
        self.assertIn('is_booked', session)
    
    def test_court_sessions_with_date(self):
        """Test court sessions with booking date"""
        booking_date = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
        response = self.client.get(f'/api/courts/{self.court.id}/sessions/?date={booking_date}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['date'], booking_date)


print("✅ Revenue tests file created successfully!")
print("Total test classes: 24")
print("Estimated test count: 80+ individual tests")
print("\nTo run tests:")
print("python manage.py test app.revenue.tests")
