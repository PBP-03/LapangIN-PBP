from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user
from app.users.models import User
from app.revenue.models import ActivityLog
from app.users.decorators import login_required, role_required, user_required, mitra_required, admin_required, anonymous_required
from app.users.utils import get_client_ip
from app.users.forms import CustomLoginForm, CustomUserCreationForm, CustomUserUpdateForm
import json


class UserModelTestCase(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        """Set up test users"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='user@test.com',
            role='user',
            first_name='Test',
            last_name='User',
            phone_number='081234567890'
        )
    
    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'user@test.com')
        self.assertEqual(self.user.role, 'user')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_str_representation(self):
        """Test user string representation"""
        expected = "testuser (User/Penyewa)"
        self.assertEqual(str(self.user), expected)


class UserUtilsTestCase(TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up request factory"""
        self.factory = RequestFactory()
    
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test getting client IP from X-Forwarded-For header"""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_without_x_forwarded_for(self):
        """Test getting client IP from REMOTE_ADDR"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')


class UserFormsTestCase(TestCase):
    """Test cases for user forms"""
    
    def test_custom_user_creation_form_valid(self):
        """Test valid user creation form"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone_number': '081234567890',
            'role': 'user'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_custom_user_creation_form_password_mismatch(self):
        """Test user creation form with mismatched passwords"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'differentpass',
            'role': 'user'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_custom_user_update_form_valid(self):
        """Test valid user update form"""
        user = User.objects.create_user(
            username='testuser2',
            password='testpass123',
            email='user@test.com',
            role='user'
        )
        
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'phone_number': '081234567890',
            'address': 'New Address'
        }
        form = CustomUserUpdateForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())


class UserDecoratorsTestCase(TestCase):
    """Test cases for user decorators"""
    
    def setUp(self):
        """Set up test users and client"""
        self.client = Client()
        self.factory = RequestFactory()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='user'
        )
        
        self.mitra = User.objects.create_user(
            username='testmitra',
            password='testpass123',
            role='mitra'
        )
        
        self.admin = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            role='admin'
        )
    
    def test_login_required_decorator_unauthenticated(self):
        """Test login_required decorator redirects unauthenticated users"""
        @login_required
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = User()  # Anonymous user
        request.user.is_authenticated = False
        
        response = test_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_login_required_decorator_authenticated(self):
        """Test login_required decorator allows authenticated users"""
        @login_required
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = self.user
        
        result = test_view(request)
        self.assertEqual(result, 'success')
    
    def test_role_required_decorator_correct_role(self):
        """Test role_required decorator with correct role"""
        @role_required('user')
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = self.user
        
        result = test_view(request)
        self.assertEqual(result, 'success')
    
    def test_user_required_decorator(self):
        """Test user_required decorator"""
        @user_required
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = self.user
        
        result = test_view(request)
        self.assertEqual(result, 'success')
    
    def test_mitra_required_decorator(self):
        """Test mitra_required decorator"""
        @mitra_required
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = self.mitra
        
        result = test_view(request)
        self.assertEqual(result, 'success')
    
    def test_admin_required_decorator(self):
        """Test admin_required decorator"""
        @admin_required
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = self.admin
        
        result = test_view(request)
        self.assertEqual(result, 'success')
    
    def test_anonymous_required_decorator_unauthenticated(self):
        """Test anonymous_required decorator allows unauthenticated users"""
        @anonymous_required()
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = User()
        request.user.is_authenticated = False
        
        result = test_view(request)
        self.assertEqual(result, 'success')
    
    def test_anonymous_required_decorator_authenticated_user(self):
        """Test anonymous_required decorator redirects authenticated user"""
        @anonymous_required()
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = self.user
        
        response = test_view(request)
        self.assertEqual(response.status_code, 302)
    
    def test_anonymous_required_decorator_authenticated_admin(self):
        """Test anonymous_required decorator redirects authenticated admin"""
        @anonymous_required()
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = self.admin
        
        response = test_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/dashboard', response.url)
    
    def test_anonymous_required_decorator_authenticated_mitra(self):
        """Test anonymous_required decorator redirects authenticated mitra"""
        @anonymous_required()
        def test_view(request):
            return 'success'
        
        request = self.factory.get('/')
        request.user = self.mitra
        
        response = test_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/mitra/dashboard', response.url)


class UserAPITestCase(TestCase):
    """Test cases for user API endpoints"""
    
    def setUp(self):
        """Set up test client and users"""
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='user@test.com',
            role='user',
            first_name='Test',
            last_name='User'
        )
    
    def test_api_login_success(self):
        """Test successful login via API"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(
            reverse('users:api_login'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['user']['username'], 'testuser')
        
        # Check that activity log was created
        self.assertTrue(ActivityLog.objects.filter(
            user=self.user,
            action_type='login'
        ).exists())
    
    def test_api_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(
            reverse('users:api_login'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_api_login_missing_fields(self):
        """Test login with missing fields"""
        data = {
            'username': 'testuser'
        }
        response = self.client.post(
            reverse('users:api_login'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_api_login_invalid_json(self):
        """Test login with invalid JSON"""
        response = self.client.post(
            reverse('users:api_login'),
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_api_register_success(self):
        """Test successful registration via API"""
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'role': 'user'
        }
        response = self.client.post(
            reverse('users:api_register'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['user']['username'], 'newuser')
        
        # Check that user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check that activity log was created
        new_user = User.objects.get(username='newuser')
        self.assertTrue(ActivityLog.objects.filter(
            user=new_user,
            action_type='create'
        ).exists())
    
    def test_api_register_invalid_data(self):
        """Test registration with invalid data"""
        data = {
            'username': 'newuser',
            'email': 'invalidemail',
            'password1': 'pass',
            'password2': 'differentpass'
        }
        response = self.client.post(
            reverse('users:api_register'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
    
    def test_api_logout_success(self):
        """Test successful logout via API"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('users:api_logout'))
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # Check that activity log was created
        self.assertTrue(ActivityLog.objects.filter(
            user=self.user,
            action_type='logout'
        ).exists())
    
    def test_api_logout_unauthenticated(self):
        """Test logout when not authenticated"""
        response = self.client.post(reverse('users:api_logout'))
        
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_api_user_status_authenticated(self):
        """Test user status API when authenticated"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:api_user_status'))
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['authenticated'])
        self.assertEqual(response_data['user']['username'], 'testuser')
    
    def test_api_user_status_unauthenticated(self):
        """Test user status API when not authenticated"""
        response = self.client.get(reverse('users:api_user_status'))
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertFalse(response_data['authenticated'])
    
    def test_api_profile_get(self):
        """Test getting user profile via API"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:api_profile'))
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['user']['username'], 'testuser')
    
    def test_api_profile_get_unauthenticated(self):
        """Test getting profile when not authenticated"""
        response = self.client.get(reverse('users:api_profile'))
        
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_api_profile_update(self):
        """Test updating user profile via API"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '081234567890',
            'address': 'New Address'
        }
        response = self.client.put(
            reverse('users:api_profile'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['user']['first_name'], 'Updated')
        
        # Check that user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        
        # Check that activity log was created
        self.assertTrue(ActivityLog.objects.filter(
            user=self.user,
            action_type='update'
        ).exists())
    
    def test_api_profile_update_username_duplicate(self):
        """Test updating profile with duplicate username"""
        # Create another user
        User.objects.create_user(
            username='existinguser',
            password='testpass123',
            email='existing@test.com',
            role='user'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'username': 'existinguser'
        }
        response = self.client.put(
            reverse('users:api_profile'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_api_profile_update_with_password(self):
        """Test updating profile with password change"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'first_name': 'Updated',
            'password': 'newpass123'
        }
        response = self.client.put(
            reverse('users:api_profile'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check that password was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
    
    def test_api_profile_delete(self):
        """Test deleting user account via API"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.delete(reverse('users:api_profile'))
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # Check that user was deleted
        self.assertFalse(User.objects.filter(username='testuser').exists())
    
    def test_api_user_dashboard_success(self):
        """Test user dashboard API with user role"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:api_user_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['user']['username'], 'testuser')
    
    def test_api_user_dashboard_unauthenticated(self):
        """Test user dashboard API when not authenticated"""
        response = self.client.get(reverse('users:api_user_dashboard'))
        
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_api_user_dashboard_wrong_role(self):
        """Test user dashboard API with wrong role"""
        admin = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            role='admin'
        )
        self.client.login(username='testadmin', password='testpass123')
        
        response = self.client.get(reverse('users:api_user_dashboard'))
        
        self.assertEqual(response.status_code, 403)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_index_view(self):
        """Test index API view"""
        response = self.client.get(reverse('users:index'))
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')

