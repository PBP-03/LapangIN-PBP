from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
import requests
from datetime import datetime, time, date, timedelta
from backend.models import (
    User, SportsCategory, Venue, VenueImage, Facility, VenueFacility,
    Court, CourtSession, CourtImage, OperationalHour, Booking, Payment, 
    Review, Pendapatan, ActivityLog
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with comprehensive sample data for LapangIN (Updated for current models)'

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

        self.stdout.write(self.style.SUCCESS('Starting comprehensive data seeding...'))
        
        # Create data in order of dependencies
        self.create_users()
        self.create_sports_categories()
        self.create_facilities()
        self.create_venues()
        self.create_venue_images()
        self.create_venue_facilities()
        self.create_courts()
        self.create_court_sessions()
        self.create_court_images()
        self.create_operational_hours()
        self.create_bookings()
        self.create_payments()
        self.create_pendapatan()
        self.create_reviews()
        self.create_activity_logs()
        
        self.stdout.write(self.style.SUCCESS('Comprehensive data seeding completed successfully!'))

    def clear_data(self):
        """Clear all existing data"""
        models_to_clear = [
            ActivityLog, Review, Pendapatan, Payment, Booking, 
            OperationalHour, CourtImage, CourtSession, Court, 
            VenueFacility, VenueImage, Venue, Facility,
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
                'profile_picture': 'https://ui-avatars.com/api/?name=Admin+LapangIN&size=128',
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
                'profile_picture': 'https://ui-avatars.com/api/?name=Ahmad+Futsal&size=128',
            },
            {
                'username': 'mitra_badminton_bandung',
                'email': 'badminton.bandung@lapangin.com',
                'first_name': 'Sari',
                'last_name': 'Badminton',
                'phone_number': '+62812-2222-2222',
                'address': 'Bandung, Jawa Barat',
                'profile_picture': 'https://ui-avatars.com/api/?name=Sari+Badminton&size=128',
            },
            {
                'username': 'mitra_basket_surabaya',
                'email': 'basket.surabaya@lapangin.com',
                'first_name': 'Budi',
                'last_name': 'Basketball',
                'phone_number': '+62812-3333-3333',
                'address': 'Surabaya, Jawa Timur',
                'profile_picture': 'https://ui-avatars.com/api/?name=Budi+Basketball&size=128',
            },
            {
                'username': 'mitra_tenis_yogya',
                'email': 'tenis.yogya@lapangin.com',
                'first_name': 'Diana',
                'last_name': 'Tennis',
                'phone_number': '+62812-4444-4444',
                'address': 'Yogyakarta, DIY',
                'profile_picture': 'https://ui-avatars.com/api/?name=Diana+Tennis&size=128',
            },
            {
                'username': 'mitra_voli_medan',
                'email': 'voli.medan@lapangin.com',
                'first_name': 'Rizki',
                'last_name': 'Volleyball',
                'phone_number': '+62812-5555-5555',
                'address': 'Medan, Sumatera Utara',
                'profile_picture': 'https://ui-avatars.com/api/?name=Rizki+Volleyball&size=128',
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
                'profile_picture': 'https://ui-avatars.com/api/?name=John+Doe&size=128',
            },
            {
                'username': 'jane_smith',
                'email': 'jane.smith@email.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone_number': '+62812-7777-7777',
                'address': 'Bandung, Jawa Barat',
                'profile_picture': 'https://ui-avatars.com/api/?name=Jane+Smith&size=128',
            },
            {
                'username': 'mike_wilson',
                'email': 'mike.wilson@email.com',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'phone_number': '+62812-8888-8888',
                'address': 'Surabaya, Jawa Timur',
                'profile_picture': 'https://ui-avatars.com/api/?name=Mike+Wilson&size=128',
            },
            {
                'username': 'sarah_johnson',
                'email': 'sarah.johnson@email.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'phone_number': '+62812-9999-9999',
                'address': 'Yogyakarta, DIY',
                'profile_picture': 'https://ui-avatars.com/api/?name=Sarah+Johnson&size=128',
            },
            {
                'username': 'david_brown',
                'email': 'david.brown@email.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'phone_number': '+62812-0000-0000',
                'address': 'Medan, Sumatera Utara',
                'profile_picture': 'https://ui-avatars.com/api/?name=David+Brown&size=128',
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
        """Create sports categories with icons"""
        self.stdout.write('Creating sports categories...')
        
        categories = [
            ('FUTSAL', 'Olahraga futsal dengan lapangan indoor', 'https://cdn-icons-png.flaticon.com/512/53/53283.png'),
            ('BADMINTON', 'Olahraga badminton dengan lapangan indoor', 'https://cdn-icons-png.flaticon.com/512/2413/2413210.png'),
            ('BASKET', 'Olahraga basket dengan lapangan indoor/outdoor', 'https://cdn-icons-png.flaticon.com/512/857/857418.png'),
            ('TENIS', 'Olahraga tenis dengan lapangan outdoor', 'https://cdn-icons-png.flaticon.com/512/2413/2413168.png'),
            ('PADEL', 'Olahraga padel dengan lapangan khusus', 'https://cdn-icons-png.flaticon.com/512/2413/2413165.png'),
            ('VOLI', 'Olahraga voli dengan lapangan indoor/outdoor', 'https://cdn-icons-png.flaticon.com/512/857/857446.png'),
        ]
        
        for name, description, icon in categories:
            category, created = SportsCategory.objects.get_or_create(
                name=name,
                defaults={'description': description, 'icon': icon}
            )

        self.stdout.write(f'Created {SportsCategory.objects.count()} sports categories')

    def create_facilities(self):
        """Create facility types with icons"""
        self.stdout.write('Creating facilities...')
        
        facilities = [
            ('Parkir Mobil', 'https://cdn-icons-png.flaticon.com/512/741/741407.png'),
            ('Parkir Motor', 'https://cdn-icons-png.flaticon.com/512/2739/2739462.png'),
            ('Toilet/WC', 'https://cdn-icons-png.flaticon.com/512/1818/1818592.png'),
            ('Kantin', 'https://cdn-icons-png.flaticon.com/512/3075/3075977.png'),
            ('Musholla', 'https://cdn-icons-png.flaticon.com/512/2736/2736581.png'),
            ('WiFi Gratis', 'https://cdn-icons-png.flaticon.com/512/159/159080.png'),
            ('AC/Kipas Angin', 'https://cdn-icons-png.flaticon.com/512/2524/2524402.png'),
            ('Ruang Ganti', 'https://cdn-icons-png.flaticon.com/512/1458/1458582.png'),
            ('Tribun Penonton', 'https://cdn-icons-png.flaticon.com/512/2936/2936719.png'),
            ('Sound System', 'https://cdn-icons-png.flaticon.com/512/727/727240.png'),
            ('Pencahayaan LED', 'https://cdn-icons-png.flaticon.com/512/702/702814.png'),
            ('CCTV', 'https://cdn-icons-png.flaticon.com/512/1005/1005141.png'),
            ('Penjaga Lapangan', 'https://cdn-icons-png.flaticon.com/512/4825/4825106.png'),
            ('Penyewaan Peralatan', 'https://cdn-icons-png.flaticon.com/512/3045/3045330.png'),
            ('Loker', 'https://cdn-icons-png.flaticon.com/512/2936/2936665.png'),
            ('Cafe/Resto', 'https://cdn-icons-png.flaticon.com/512/3075/3075977.png'),
            ('Area Istirahat', 'https://cdn-icons-png.flaticon.com/512/2936/2936785.png'),
            ('Shower', 'https://cdn-icons-png.flaticon.com/512/1818/1818665.png'),
            ('First Aid Kit', 'https://cdn-icons-png.flaticon.com/512/883/883407.png'),
            ('Lapangan Berkualitas Sintetis', 'https://cdn-icons-png.flaticon.com/512/2413/2413048.png'),
        ]
        
        for facility_name, icon_url in facilities:
            facility, created = Facility.objects.get_or_create(
                name=facility_name,
                defaults={
                    'description': f'Fasilitas {facility_name} tersedia di venue',
                    'icon': icon_url
                }
            )

        self.stdout.write(f'Created {Facility.objects.count()} facilities')

    def create_venues(self):
        """Create venues with realistic data"""
        self.stdout.write('Creating venues...')
        
        # Get users and admin
        admin = User.objects.filter(role='admin').first()
        
        venues_data = [
            # Futsal venues
            {
                'name': 'Futsal Arena Jakarta',
                'owner': 'mitra_futsal_jakarta',
                'address': 'Jl. Sudirman No. 123, Jakarta Selatan, DKI Jakarta',
                'location_url': 'https://maps.google.com/futsal-arena-jakarta',
                'contact': '+62812-1111-1111',
                'description': 'Lapangan futsal modern dengan fasilitas lengkap di pusat Jakarta. Lantai sintetis berkualitas tinggi, pencahayaan LED, dan AC.',
                'number_of_courts': 3,
            },
            {
                'name': 'Champion Futsal Center',
                'owner': 'mitra_futsal_jakarta',
                'address': 'Jl. Kemang Raya No. 45, Jakarta Selatan, DKI Jakarta',
                'location_url': 'https://maps.google.com/champion-futsal',
                'contact': '+62812-1111-2222',
                'description': 'Futsal center dengan 4 lapangan berkualitas internasional. Dilengkapi kantin, parkir luas, dan ruang ganti.',
                'number_of_courts': 4,
            },
            
            # Badminton venues
            {
                'name': 'Shuttle Court Bandung',
                'owner': 'mitra_badminton_bandung',
                'address': 'Jl. Dago No. 67, Bandung, Jawa Barat',
                'location_url': 'https://maps.google.com/shuttle-court-bandung',
                'contact': '+62812-2222-2222',
                'description': 'Lapangan badminton premium dengan karpet BWF standard. 8 lapangan indoor dengan AC dan pencahayaan profesional.',
                'number_of_courts': 8,
            },
            {
                'name': 'Bandung Badminton Hall',
                'owner': 'mitra_badminton_bandung',
                'address': 'Jl. Pasteur No. 89, Bandung, Jawa Barat',
                'location_url': 'https://maps.google.com/badminton-hall-bandung',
                'contact': '+62812-2222-3333',
                'description': 'Hall badminton dengan 12 lapangan. Fasilitas lengkap termasuk cafe, pro shop, dan area spectator.',
                'number_of_courts': 12,
            },
            
            # Basketball venues
            {
                'name': 'Surabaya Basketball Complex',
                'owner': 'mitra_basket_surabaya',
                'address': 'Jl. Ahmad Yani No. 234, Surabaya, Jawa Timur',
                'location_url': 'https://maps.google.com/basketball-surabaya',
                'contact': '+62812-3333-3333',
                'description': 'Kompleks basket outdoor dan indoor dengan standar internasional. Ring adjustable, lantai kayu parket.',
                'number_of_courts': 2,
            },
            {
                'name': 'Urban Basketball Court',
                'owner': 'mitra_basket_surabaya',
                'address': 'Jl. Pemuda No. 156, Surabaya, Jawa Timur',
                'location_url': 'https://maps.google.com/urban-basketball',
                'contact': '+62812-3333-4444',
                'description': 'Lapangan basket urban style dengan suasana street basketball. Outdoor court dengan floodlight malam.',
                'number_of_courts': 1,
            },
            
            # Tennis venues
            {
                'name': 'Yogya Tennis Club',
                'owner': 'mitra_tenis_yogya',
                'address': 'Jl. Malioboro No. 78, Yogyakarta, DIY',
                'location_url': 'https://maps.google.com/yogya-tennis',
                'contact': '+62812-4444-4444',
                'description': 'Klub tenis eksklusif dengan lapangan clay dan hard court. Fasilitas club house dan pelatih tersedia.',
                'number_of_courts': 6,
            },
            
            # Volleyball venues
            {
                'name': 'Medan Volleyball Arena',
                'owner': 'mitra_voli_medan',
                'address': 'Jl. Gatot Subroto No. 45, Medan, Sumatera Utara',
                'location_url': 'https://maps.google.com/medan-volleyball',
                'contact': '+62812-5555-5555',
                'description': 'Arena voli indoor dengan net profesional dan lantai khusus voli. Kapasitas spectator 200 orang.',
                'number_of_courts': 3,
            },
            
            # Additional premium venues
            {
                'name': 'Elite Futsal Jakarta',
                'owner': 'mitra_futsal_jakarta',
                'address': 'Jl. Thamrin No. 90, Jakarta Pusat, DKI Jakarta',
                'location_url': 'https://maps.google.com/elite-futsal',
                'contact': '+62812-1111-5555',
                'description': 'Futsal premium dengan teknologi terbaru. Booking system digital, live streaming, dan virtual reality corner.',
                'number_of_courts': 2,
            },
            {
                'name': 'Smash Badminton Bandung',
                'owner': 'mitra_badminton_bandung',
                'address': 'Jl. Setiabudhi No. 123, Bandung, Jawa Barat',
                'location_url': 'https://maps.google.com/smash-badminton',
                'contact': '+62812-2222-6666',
                'description': 'Lapangan badminton dengan kualitas tournament grade. Sistem ventilasi terbaik dan no-echo sound system.',
                'number_of_courts': 6,
            },
        ]
        
        for venue_data in venues_data:
            owner = User.objects.get(username=venue_data['owner'])
            
            venue, created = Venue.objects.get_or_create(
                name=venue_data['name'],
                defaults={
                    'owner': owner,
                    'address': venue_data['address'],
                    'location_url': venue_data['location_url'],
                    'contact': venue_data['contact'],
                    'description': venue_data['description'],
                    'number_of_courts': venue_data['number_of_courts'],
                    'verification_status': 'approved',
                    'verified_by': admin,
                    'verification_date': timezone.now(),
                }
            )

        self.stdout.write(f'Created {Venue.objects.count()} venues')

    def create_venue_images(self):
        """Create venue images"""
        self.stdout.write('Creating venue images...')
        
        # Sample venue images for different sports
        venue_images = {
            'futsal': [
                'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=800',
                'https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=800',
                'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800',
            ],
            'badminton': [
                'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800',
                'https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800',
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800',
            ],
            'basketball': [
                'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800',
                'https://images.unsplash.com/photo-1574623452334-1e0ac2b3ccb4?w=800',
                'https://images.unsplash.com/photo-1627627256672-027a4613d028?w=800',
            ],
            'tennis': [
                'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=800',
                'https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=800',
                'https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=800',
            ],
            'volleyball': [
                'https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800',
                'https://images.unsplash.com/photo-1594736797933-d0300bdc39a0?w=800',
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800',
            ],
        }
        
        venues = Venue.objects.all()
        
        for venue in venues:
            # Determine sport type from venue name
            sport_type = 'futsal'  # default
            if 'badminton' in venue.name.lower() or 'shuttle' in venue.name.lower() or 'smash' in venue.name.lower():
                sport_type = 'badminton'
            elif 'basket' in venue.name.lower():
                sport_type = 'basketball'
            elif 'tenis' in venue.name.lower():
                sport_type = 'tennis'
            elif 'voli' in venue.name.lower():
                sport_type = 'volleyball'
            
            # Create 2-3 images per venue
            images = venue_images.get(sport_type, venue_images['futsal'])
            num_images = random.randint(2, min(3, len(images)))
            selected_images = random.sample(images, num_images)
            
            for i, image_url in enumerate(selected_images):
                VenueImage.objects.create(
                    venue=venue,
                    image_url=image_url,
                    is_primary=(i == 0),  # First image is primary
                    caption=f"{venue.name} - Gambar {i+1}"
                )

        self.stdout.write(f'Created {VenueImage.objects.count()} venue images')

    def create_venue_facilities(self):
        """Assign facilities to venues"""
        self.stdout.write('Creating venue facilities...')
        
        venues = Venue.objects.all()
        facilities = list(Facility.objects.all())
        
        for venue in venues:
            # Each venue gets 8-12 random facilities
            num_facilities = random.randint(8, 12)
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
        
        venues = Venue.objects.all()
        categories = {
            'FUTSAL': SportsCategory.objects.get(name='FUTSAL'),
            'BADMINTON': SportsCategory.objects.get(name='BADMINTON'),
            'BASKET': SportsCategory.objects.get(name='BASKET'),
            'TENIS': SportsCategory.objects.get(name='TENIS'),
            'VOLI': SportsCategory.objects.get(name='VOLI'),
        }
        
        # Price mapping based on sport type
        price_ranges = {
            'FUTSAL': (120000, 250000),
            'BADMINTON': (60000, 120000),
            'BASKET': (100000, 300000),
            'TENIS': (80000, 150000),
            'VOLI': (100000, 200000),
        }
        
        for venue in venues:
            # Determine sport category from venue name
            category = categories['FUTSAL']  # default
            price_range = price_ranges['FUTSAL']
            
            if 'badminton' in venue.name.lower() or 'shuttle' in venue.name.lower() or 'smash' in venue.name.lower():
                category = categories['BADMINTON']
                price_range = price_ranges['BADMINTON']
            elif 'basket' in venue.name.lower():
                category = categories['BASKET']
                price_range = price_ranges['BASKET']
            elif 'tenis' in venue.name.lower():
                category = categories['TENIS']
                price_range = price_ranges['TENIS']
            elif 'voli' in venue.name.lower():
                category = categories['VOLI']
                price_range = price_ranges['VOLI']
            
            # Create courts for this venue
            for i in range(venue.number_of_courts):
                court_name = f"Court {i+1}" if venue.number_of_courts <= 10 else f"Court {chr(65+i)}"  # A, B, C for many courts
                price = Decimal(str(random.randint(price_range[0], price_range[1])))
                
                Court.objects.create(
                    venue=venue,
                    name=court_name,
                    category=category,
                    price_per_hour=price,
                    is_active=True,
                    description=f"Lapangan {category.get_name_display()} standar internasional dengan fasilitas lengkap"
                )

        self.stdout.write(f'Created {Court.objects.count()} courts')

    def create_court_sessions(self):
        """Create court sessions/time slots"""
        self.stdout.write('Creating court sessions...')
        
        courts = Court.objects.all()
        
        # Standard time sessions
        sessions = [
            ('Morning Session', time(6, 0), time(12, 0)),
            ('Afternoon Session', time(12, 0), time(18, 0)),
            ('Evening Session', time(18, 0), time(24, 0)),
        ]
        
        # Hourly sessions for more detailed booking
        hourly_sessions = []
        for hour in range(6, 24):  # 6 AM to 11 PM
            start_time = time(hour, 0)
            end_time = time(hour + 1, 0) if hour < 23 else time(23, 59)
            hourly_sessions.append((f"Session {hour:02d}:00", start_time, end_time))
        
        for court in courts:
            # Create both general sessions and hourly sessions
            all_sessions = sessions + random.sample(hourly_sessions, 10)  # Add 10 random hourly sessions
            
            for session_name, start_time, end_time in all_sessions:
                CourtSession.objects.get_or_create(
                    court=court,
                    start_time=start_time,
                    defaults={
                        'session_name': session_name,
                        'end_time': end_time,
                        'is_active': True
                    }
                )

        self.stdout.write(f'Created {CourtSession.objects.count()} court sessions')

    def create_court_images(self):
        """Create court images"""
        self.stdout.write('Creating court images...')
        
        courts = Court.objects.all()
        
        # Sample court images based on sport category
        sport_images = {
            'FUTSAL': [
                'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=600',
                'https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=600',
            ],
            'BADMINTON': [
                'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600',
                'https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=600',
            ],
            'BASKET': [
                'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=600',
                'https://images.unsplash.com/photo-1574623452334-1e0ac2b3ccb4?w=600',
            ],
            'TENIS': [
                'https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=600',
                'https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=600',
            ],
            'VOLI': [
                'https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=600',
                'https://images.unsplash.com/photo-1594736797933-d0300bdc39a0?w=600',
            ],
        }
        
        for court in courts:
            category_name = court.category.name if court.category else 'FUTSAL'
            images = sport_images.get(category_name, sport_images['FUTSAL'])
            
            # Create 1-2 images per court
            num_images = random.randint(1, 2)
            selected_images = random.sample(images, min(num_images, len(images)))
            
            for i, image_url in enumerate(selected_images):
                CourtImage.objects.create(
                    court=court,
                    image_url=image_url,
                    is_primary=(i == 0),
                    caption=f"{court.name} - Detail View {i+1}"
                )

        self.stdout.write(f'Created {CourtImage.objects.count()} court images')

    def create_operational_hours(self):
        """Create operational hours for venues"""
        self.stdout.write('Creating operational hours...')
        
        venues = Venue.objects.all()
        
        for venue in venues:
            for day in range(7):  # Monday to Sunday
                # Most venues operate 6 AM to 11 PM
                open_time = time(6, 0)
                close_time = time(23, 0)
                
                # Some variation for weekends
                if day in [5, 6]:  # Saturday, Sunday
                    if random.choice([True, False]):
                        open_time = time(7, 0)  # Open later on weekends sometimes
                
                OperationalHour.objects.create(
                    venue=venue,
                    day_of_week=day,
                    open_time=open_time,
                    close_time=close_time,
                    is_closed=False
                )

        self.stdout.write(f'Created {OperationalHour.objects.count()} operational hour entries')

    def create_bookings(self):
        """Create sample bookings"""
        self.stdout.write('Creating bookings...')
        
        users = list(User.objects.filter(role='user'))
        courts = list(Court.objects.all())
        
        # Create bookings for the past month and next month
        start_date = date.today() - timedelta(days=30)
        end_date = date.today() + timedelta(days=30)
        
        booking_count = 0
        current_date = start_date
        
        while current_date <= end_date and booking_count < 100:  # Create up to 100 bookings
            if random.random() < 0.4:  # 40% chance of booking on any given day
                # Create 1-3 bookings per day
                daily_bookings = random.randint(1, 3)
                
                for _ in range(daily_bookings):
                    user = random.choice(users)
                    court = random.choice(courts)
                    
                    # Random booking time between 6 AM and 10 PM
                    start_hour = random.randint(6, 22)
                    start_time = time(start_hour, 0)
                    
                    # Duration 1-3 hours
                    duration = random.choice([1, 1.5, 2, 2.5, 3])
                    end_hour = start_hour + int(duration)
                    end_minute = int((duration % 1) * 60)
                    end_time = time(min(end_hour, 23), end_minute)
                    
                    total_price = court.price_per_hour * Decimal(str(duration))
                    
                    # Status based on date
                    if current_date < date.today():
                        booking_status = random.choice(['completed', 'completed', 'cancelled'])
                        payment_status = 'paid' if booking_status == 'completed' else random.choice(['unpaid', 'refunded'])
                    elif current_date == date.today():
                        booking_status = random.choice(['confirmed', 'pending'])
                        payment_status = random.choice(['paid', 'unpaid'])
                    else:
                        booking_status = 'pending'
                        payment_status = 'unpaid'
                    
                    try:
                        booking = Booking.objects.create(
                            user=user,
                            court=court,
                            booking_date=current_date,
                            start_time=start_time,
                            end_time=end_time,
                            duration_hours=Decimal(str(duration)),
                            total_price=total_price,
                            booking_status=booking_status,
                            payment_status=payment_status,
                            notes=f"Booking untuk {court.category.get_name_display() if court.category else 'olahraga'}" if random.choice([True, False]) else None
                        )
                        booking_count += 1
                    except:
                        # Skip if there's a conflict (same court, date, time)
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
                payment_proof=f'https://example.com/payment-proof/{random.randint(1000, 9999)}.jpg' if random.choice([True, False]) else None,
                verified_by=admin if random.choice([True, False]) else None,
                notes=f'Pembayaran via {random.choice(["BCA", "Mandiri", "OVO", "GoPay", "DANA"])}' if random.choice([True, False]) else None,
                paid_at=booking.created_at + timedelta(minutes=random.randint(5, 120))
            )

        self.stdout.write(f'Created {Payment.objects.count()} payments')

    def create_pendapatan(self):
        """Create pendapatan records for completed bookings"""
        self.stdout.write('Creating pendapatan records...')
        
        completed_bookings = Booking.objects.filter(booking_status='completed', payment_status='paid')
        
        for booking in completed_bookings:
            mitra = booking.court.venue.owner
            
            Pendapatan.objects.create(
                mitra=mitra,
                booking=booking,
                amount=booking.total_price,
                commission_rate=Decimal('10.00'),  # 10% commission
                payment_status='paid' if random.choice([True, True, False]) else 'pending',  # 66% chance paid
                paid_at=booking.created_at + timedelta(days=random.randint(1, 7)) if random.choice([True, False]) else None,
                notes=f'Pendapatan dari booking {booking.court.venue.name} - {booking.court.name}'
            )

        self.stdout.write(f'Created {Pendapatan.objects.count()} pendapatan records')

    def create_reviews(self):
        """Create reviews for completed bookings"""
        self.stdout.write('Creating reviews...')
        
        completed_bookings = Booking.objects.filter(booking_status='completed')
        
        review_comments = [
            "Lapangan bagus, fasilitas lengkap dan bersih!",
            "Pelayanan memuaskan, pasti akan booking lagi.",
            "Fasilitas OK, lokasi strategis dan mudah dijangkau.",
            "Lapangan berkualitas, harga sesuai dengan fasilitas.",
            "Overall good experience, recommended!",
            "Tempatnya nyaman, parkirnya luas.",
            "Lapangannya mantap, AC dingin, lighting bagus.",
            "Staff ramah dan responsif, terima kasih!",
            "Toilet bersih, ada kantin juga. Lengkap!",
            "Booking mudah, pembayaran fleksibel.",
            "Kualitas lapangan sesuai ekspektasi.",
            "Tempat favorit untuk main bareng teman-teman.",
            "Fasilitasnya lengkap, dari parkir sampai shower.",
            "Pelayanannya bagus, akan merekomendasikan ke teman.",
            "Lapangan standar internasional, puas main di sini.",
        ]
        
        # Create reviews for 60% of completed bookings
        for booking in random.sample(list(completed_bookings), int(len(completed_bookings) * 0.6)):
            Review.objects.create(
                booking=booking,
                rating=random.choices([3, 4, 5], weights=[10, 40, 50])[0],  # Weighted towards higher ratings
                comment=random.choice(review_comments),
            )

        self.stdout.write(f'Created {Review.objects.count()} reviews')

    def create_activity_logs(self):
        """Create activity logs"""
        self.stdout.write('Creating activity logs...')
        
        users = list(User.objects.all())
        actions = ['login', 'logout', 'booking', 'payment', 'create', 'update']
        
        # Create logs for the past 30 days
        for _ in range(200):  # Create 200 activity logs
            user = random.choice(users)
            action = random.choice(actions)
            
            # Generate appropriate descriptions based on action
            descriptions = {
                'login': f'{user.username} logged into the system',
                'logout': f'{user.username} logged out of the system',
                'booking': f'{user.username} created a new booking',
                'payment': f'{user.username} made a payment',
                'create': f'{user.username} created new data',
                'update': f'{user.username} updated data',
            }
            
            # Random timestamp in the past 30 days
            random_date = timezone.now() - timedelta(days=random.randint(0, 30))
            
            log = ActivityLog(
                user=user,
                action_type=action,
                description=descriptions[action],
                ip_address=f'192.168.1.{random.randint(1, 254)}',
                user_agent='Mozilla/5.0 (compatible; LapangIN/1.0)',
                timestamp=random_date
            )
            log.save()

        self.stdout.write(f'Created {ActivityLog.objects.count()} activity logs')