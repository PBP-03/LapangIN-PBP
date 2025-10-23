from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
from datetime import datetime, time, date, timedelta
from backend.models import (
    User, SportsCategory, Venue, Facility, VenueFacility,
    Court, OperationalHour, Booking, Payment, Review, ActivityLog
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample data for LapangIN (Simple version without images)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting simple data seeding...'))
        
        # Create data in order of dependencies
        self.create_users()
        self.create_sports_categories()
        self.create_facilities()
        self.create_venues()
        self.create_venue_facilities()
        self.create_courts()
        self.create_operational_hours()
        self.create_bookings()
        self.create_payments()
        self.create_reviews()
        self.create_activity_logs()
        
        self.stdout.write(self.style.SUCCESS('Simple data seeding completed successfully!'))

    def clear_data(self):
        """Clear all existing data"""
        models_to_clear = [
            ActivityLog, Review, Payment, Booking, OperationalHour,
            Court, VenueFacility, Venue, Facility,
            SportsCategory, User
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'Cleared {count} {model.__name__} records')

    def create_users(self):
        """Create sample users with different roles"""
        self.stdout.write('Creating users...')
        
        # Create superuser/admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@lapangin.com',
                'first_name': 'Admin',
                'last_name': 'LapangIN',
                'role': 'admin',
                'phone_number': '+62812-3456-7890',
                'address': 'Jakarta, Indonesia',
                'is_verified': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        # Create mitra users
        mitra_data = [
            {
                'username': 'mitra_futsal_jakarta',
                'email': 'futsal.jakarta@lapangin.com',
                'first_name': 'Ahmad',
                'last_name': 'Futsal',
                'phone_number': '+62812-1111-1111',
                'address': 'Jakarta Selatan, DKI Jakarta',
            },
            {
                'username': 'mitra_badminton_bandung',
                'email': 'badminton.bandung@lapangin.com',
                'first_name': 'Sari',
                'last_name': 'Badminton',
                'phone_number': '+62812-2222-2222',
                'address': 'Bandung, Jawa Barat',
            },
            {
                'username': 'mitra_basket_surabaya',
                'email': 'basket.surabaya@lapangin.com',
                'first_name': 'Budi',
                'last_name': 'Basketball',
                'phone_number': '+62812-3333-3333',
                'address': 'Surabaya, Jawa Timur',
            },
        ]

        for data in mitra_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    **data,
                    'role': 'mitra',
                    'is_verified': True,
                }
            )
            if created:
                user.set_password('mitra123')
                user.save()

        # Create regular users
        user_data = [
            {
                'username': 'john_doe',
                'email': 'john.doe@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+62812-6666-6666',
                'address': 'Jakarta Utara, DKI Jakarta',
            },
            {
                'username': 'jane_smith',
                'email': 'jane.smith@email.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone_number': '+62812-7777-7777',
                'address': 'Bandung, Jawa Barat',
            },
            {
                'username': 'mike_wilson',
                'email': 'mike.wilson@email.com',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'phone_number': '+62812-8888-8888',
                'address': 'Surabaya, Jawa Timur',
            },
        ]

        for data in user_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    **data,
                    'role': 'user',
                    'is_verified': True,
                }
            )
            if created:
                user.set_password('user123')
                user.save()

        self.stdout.write(f'Created {User.objects.count()} users')

    def create_sports_categories(self):
        """Create sports categories"""
        self.stdout.write('Creating sports categories...')
        
        categories = [
            ('FUTSAL', 'Olahraga futsal dengan lapangan indoor'),
            ('BADMINTON', 'Olahraga badminton dengan lapangan indoor'),
            ('BASKET', 'Olahraga basket dengan lapangan indoor/outdoor'),
            ('TENIS', 'Olahraga tenis dengan lapangan outdoor'),
            ('VOLI', 'Olahraga voli dengan lapangan indoor/outdoor'),
        ]
        
        for name, description in categories:
            category, created = SportsCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )

        self.stdout.write(f'Created {SportsCategory.objects.count()} sports categories')

    def create_facilities(self):
        """Create facility types"""
        self.stdout.write('Creating facilities...')
        
        facilities = [
            'Parkir Mobil', 'Parkir Motor', 'Toilet/WC', 'Kantin', 'Musholla',
            'WiFi Gratis', 'AC/Kipas Angin', 'Ruang Ganti', 'Tribun Penonton',
            'Sound System', 'Pencahayaan LED', 'CCTV', 'Penjaga Lapangan',
            'Penyewaan Peralatan', 'Loker', 'Area Istirahat', 'Shower',
        ]
        
        for facility_name in facilities:
            facility, created = Facility.objects.get_or_create(
                name=facility_name,
                defaults={'description': f'Fasilitas {facility_name} tersedia di venue'}
            )

        self.stdout.write(f'Created {Facility.objects.count()} facilities')

    def create_venues(self):
        """Create venues with realistic data"""
        self.stdout.write('Creating venues...')
        
        # Get users
        admin = User.objects.filter(role='admin').first()
        
        venues_data = [
            {
                'name': 'Futsal Arena Jakarta',
                'owner': 'mitra_futsal_jakarta',
                'address': 'Jl. Sudirman No. 123, Jakarta Selatan, DKI Jakarta',
                'description': 'Lapangan futsal modern dengan fasilitas lengkap di pusat Jakarta.',
                'number_of_courts': 3,
                'courts_config': [
                    {'name': 'Court 1', 'category': 'FUTSAL', 'price': Decimal('150000')},
                    {'name': 'Court 2', 'category': 'FUTSAL', 'price': Decimal('150000')},
                    {'name': 'Court 3', 'category': 'FUTSAL', 'price': Decimal('180000')},
                ]
            },
            {
                'name': 'Shuttle Court Bandung',
                'owner': 'mitra_badminton_bandung',
                'address': 'Jl. Dago No. 67, Bandung, Jawa Barat',
                'description': 'Lapangan badminton premium dengan karpet BWF standard.',
                'number_of_courts': 8,
                'courts_config': [
                    {'name': f'Court {i+1}', 'category': 'BADMINTON', 'price': Decimal('80000')} 
                    for i in range(8)
                ]
            },
            {
                'name': 'Surabaya Basketball Complex',
                'owner': 'mitra_basket_surabaya',
                'address': 'Jl. Ahmad Yani No. 234, Surabaya, Jawa Timur',
                'description': 'Kompleks basket dengan standar internasional.',
                'number_of_courts': 2,
                'courts_config': [
                    {'name': 'Court A', 'category': 'BASKET', 'price': Decimal('200000')},
                    {'name': 'Court B', 'category': 'BASKET', 'price': Decimal('200000')},
                ]
            },
            {
                'name': 'Elite Futsal Jakarta',
                'owner': 'mitra_futsal_jakarta',
                'address': 'Jl. Thamrin No. 90, Jakarta Pusat, DKI Jakarta',
                'description': 'Futsal premium dengan teknologi terbaru.',
                'number_of_courts': 2,
                'courts_config': [
                    {'name': 'Premium Court 1', 'category': 'FUTSAL', 'price': Decimal('220000')},
                    {'name': 'Premium Court 2', 'category': 'FUTSAL', 'price': Decimal('220000')},
                ]
            },
        ]
        
        for venue_data in venues_data:
            owner = User.objects.get(username=venue_data['owner'])
            
            venue, created = Venue.objects.get_or_create(
                name=venue_data['name'],
                defaults={
                    'owner': owner,
                    'address': venue_data['address'],
                    'description': venue_data['description'],
                    'number_of_courts': venue_data['number_of_courts'],
                    'verification_status': 'approved',
                    'verified_by': admin,
                    'verification_date': timezone.now(),
                    'contact': '+62812-1234-5678',
                    'location_url': f'https://maps.google.com/{venue_data["name"].lower().replace(" ", "-")}',
                }
            )
            
            # Store courts config for later use in create_courts
            if created:
                venue._courts_config = venue_data['courts_config']

        self.stdout.write(f'Created {Venue.objects.count()} venues')

    def create_venue_facilities(self):
        """Assign facilities to venues"""
        self.stdout.write('Creating venue facilities...')
        
        venues = Venue.objects.all()
        facilities = list(Facility.objects.all())
        
        for venue in venues:
            # Each venue gets 5-8 random facilities
            num_facilities = random.randint(5, 8)
            selected_facilities = random.sample(facilities, min(num_facilities, len(facilities)))
            
            for facility in selected_facilities:
                VenueFacility.objects.get_or_create(
                    venue=venue,
                    facility=facility
                )

        self.stdout.write(f'Created {VenueFacility.objects.count()} venue-facility relationships')

    def create_courts(self):
        """Create individual courts for each venue"""
        self.stdout.write('Creating courts...')
        
        # Define courts configuration
        venues_courts_config = {
            'Futsal Arena Jakarta': [
                {'name': 'Court 1', 'category': 'FUTSAL', 'price': Decimal('150000')},
                {'name': 'Court 2', 'category': 'FUTSAL', 'price': Decimal('150000')},
                {'name': 'Court 3', 'category': 'FUTSAL', 'price': Decimal('180000')},
            ],
            'Shuttle Court Bandung': [
                {'name': f'Court {i+1}', 'category': 'BADMINTON', 'price': Decimal('80000')} 
                for i in range(8)
            ],
            'Surabaya Basketball Complex': [
                {'name': 'Court A', 'category': 'BASKET', 'price': Decimal('200000')},
                {'name': 'Court B', 'category': 'BASKET', 'price': Decimal('200000')},
            ],
            'Elite Futsal Jakarta': [
                {'name': 'Premium Court 1', 'category': 'FUTSAL', 'price': Decimal('220000')},
                {'name': 'Premium Court 2', 'category': 'FUTSAL', 'price': Decimal('220000')},
            ],
        }
        
        venues = Venue.objects.all()
        
        for venue in venues:
            courts_config = venues_courts_config.get(venue.name, [])
            
            if courts_config:
                for court_data in courts_config:
                    category = SportsCategory.objects.get(name=court_data['category'])
                    
                    Court.objects.get_or_create(
                        venue=venue,
                        name=court_data['name'],
                        defaults={
                            'category': category,
                            'price_per_hour': court_data['price'],
                            'is_active': True
                        }
                    )
            else:
                # Fallback: create default courts if no config
                for i in range(venue.number_of_courts):
                    court_name = f"Court {i+1}" if venue.number_of_courts > 1 else "Main Court"
                    
                    # Try to get a default category (FUTSAL)
                    default_category = SportsCategory.objects.filter(name='FUTSAL').first()
                    
                    Court.objects.get_or_create(
                        venue=venue,
                        name=court_name,
                        defaults={
                            'category': default_category,
                            'price_per_hour': Decimal('100000'),
                            'is_active': True
                        }
                    )

        self.stdout.write(f'Created {Court.objects.count()} courts')

    def create_operational_hours(self):
        """Create operational hours for venues"""
        self.stdout.write('Creating operational hours...')
        
        venues = Venue.objects.all()
        
        for venue in venues:
            for day in range(7):
                OperationalHour.objects.get_or_create(
                    venue=venue,
                    day_of_week=day,
                    defaults={
                        'open_time': time(6, 0),
                        'close_time': time(23, 0),
                        'is_closed': False,
                    }
                )

        self.stdout.write(f'Created {OperationalHour.objects.count()} operational hour entries')

    def create_bookings(self):
        """Create sample bookings"""
        self.stdout.write('Creating bookings...')
        
        users = list(User.objects.filter(role='user'))
        courts = list(Court.objects.all())
        
        # Create bookings for the past week and next week
        start_date = date.today() - timedelta(days=7)
        end_date = date.today() + timedelta(days=7)
        
        booking_count = 0
        current_date = start_date
        
        while current_date <= end_date and booking_count < 30:
            if random.random() < 0.6:  # 60% chance of bookings per day
                daily_bookings = random.randint(1, 3)
                
                for _ in range(daily_bookings):
                    user = random.choice(users)
                    court = random.choice(courts)
                    
                    start_hour = random.randint(8, 20)
                    start_time = time(start_hour, 0)
                    duration = random.choice([1, 2, 3])
                    end_time = time(start_hour + duration, 0)
                    
                    if start_hour + duration <= 23:
                        total_price = court.price_per_hour * Decimal(str(duration))
                        
                        status = 'completed' if current_date < date.today() else 'confirmed'
                        payment_status = 'paid' if status == 'completed' else 'unpaid'
                        
                        try:
                            booking = Booking.objects.create(
                                user=user,
                                court=court,
                                booking_date=current_date,
                                start_time=start_time,
                                end_time=end_time,
                                duration_hours=Decimal(str(duration)),
                                total_price=total_price,
                                booking_status=status,
                                payment_status=payment_status,
                            )
                            booking_count += 1
                        except Exception:
                            pass
            
            current_date += timedelta(days=1)

        self.stdout.write(f'Created {Booking.objects.count()} bookings')

    def create_payments(self):
        """Create payments for paid bookings"""
        self.stdout.write('Creating payments...')
        
        paid_bookings = Booking.objects.filter(payment_status='paid')
        admin = User.objects.filter(role='admin').first()
        
        for booking in paid_bookings:
            Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                payment_method=random.choice(['bank_transfer', 'e_wallet', 'credit_card']),
                transaction_id=f'TXN{random.randint(100000, 999999)}',
                verified_by=admin,
                paid_at=booking.created_at + timedelta(minutes=30)
            )

        self.stdout.write(f'Created {Payment.objects.count()} payments')

    def create_reviews(self):
        """Create reviews for completed bookings"""
        self.stdout.write('Creating reviews...')
        
        completed_bookings = Booking.objects.filter(booking_status='completed')
        
        review_comments = [
            "Lapangan bagus, fasilitas lengkap!",
            "Pelayanan memuaskan, recommended.",
            "Fasilitas OK, lokasi strategis.",
            "Lapangan berkualitas, harga sesuai.",
            "Good experience overall!",
        ]
        
        for booking in completed_bookings[:15]:  # Review first 15 completed bookings
            Review.objects.create(
                booking=booking,
                rating=random.randint(3, 5),
                comment=random.choice(review_comments),
            )

        self.stdout.write(f'Created {Review.objects.count()} reviews')

    def create_activity_logs(self):
        """Create activity logs"""
        self.stdout.write('Creating activity logs...')
        
        users = list(User.objects.all())
        actions = ['login', 'logout', 'booking', 'payment']
        
        for _ in range(50):
            user = random.choice(users)
            action = random.choice(actions)
            
            ActivityLog.objects.create(
                user=user,
                action_type=action,
                description=f'User {user.username} performed {action}',
                ip_address=f'192.168.1.{random.randint(1, 254)}',
            )

        self.stdout.write(f'Created {ActivityLog.objects.count()} activity logs')