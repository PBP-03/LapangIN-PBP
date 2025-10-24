from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from decimal import Decimal
import requests
import random
from datetime import datetime, time, date, timedelta

# Import from new apps
from app.users.models import User
from app.venues.models import SportsCategory, Venue, VenueImage, Facility, VenueFacility, OperationalHour
from app.courts.models import Court
from app.bookings.models import Booking, Payment
from app.reviews.models import Review
from app.revenue.models import ActivityLog

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample data for LapangIN'

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

        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))
        
        # Create data in order of dependencies
        self.create_users()
        self.create_sports_categories()
        self.create_facilities()
        self.create_venues()
        self.create_venue_images()
        self.create_venue_facilities()
        self.create_courts()
        self.create_operational_hours()
        self.create_bookings()
        self.create_payments()
        self.create_reviews()
        self.create_activity_logs()
        
        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))

    def clear_data(self):
        """Clear all existing data"""
        models_to_clear = [
            ActivityLog, Review, Payment, Booking, OperationalHour,
            Court, VenueFacility, VenueImage, Venue, Facility,
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
            {
                'username': 'mitra_tenis_yogya',
                'email': 'tenis.yogya@lapangin.com',
                'first_name': 'Diana',
                'last_name': 'Tennis',
                'phone_number': '+62812-4444-4444',
                'address': 'Yogyakarta, DIY',
            },
            {
                'username': 'mitra_voli_medan',
                'email': 'voli.medan@lapangin.com',
                'first_name': 'Rizki',
                'last_name': 'Volleyball',
                'phone_number': '+62812-5555-5555',
                'address': 'Medan, Sumatera Utara',
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
            {
                'username': 'sarah_johnson',
                'email': 'sarah.johnson@email.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'phone_number': '+62812-9999-9999',
                'address': 'Yogyakarta, DIY',
            },
            {
                'username': 'david_brown',
                'email': 'david.brown@email.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'phone_number': '+62812-0000-0000',
                'address': 'Medan, Sumatera Utara',
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
            ('PADEL', 'Olahraga padel dengan lapangan khusus'),
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
            'Parkir Mobil',
            'Parkir Motor', 
            'Toilet/WC',
            'Kantin',
            'Musholla',
            'WiFi Gratis',
            'AC/Kipas Angin',
            'Ruang Ganti',
            'Tribun Penonton',
            'Sound System',
            'Pencahayaan LED',
            'CCTV',
            'Penjaga Lapangan',
            'Penyewaan Peralatan',
            'Loker',
            'Cafe/Resto',
            'Area Istirahat',
            'Shower',
            'First Aid Kit',
            'Lapangan Berkualitas Sintetis',
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
        
        # Get users and categories
        mitras = User.objects.filter(role='mitra')
        admin = User.objects.filter(role='admin').first()
        categories = SportsCategory.objects.all()
        
        venues_data = [
            # Futsal venues
            {
                'name': 'Futsal Arena Jakarta',
                'category': 'FUTSAL',
                'owner': 'mitra_futsal_jakarta',
                'address': 'Jl. Sudirman No. 123, Jakarta Selatan, DKI Jakarta',
                'location_url': 'https://maps.google.com/futsal-arena-jakarta',
                'contact': '+62812-1111-1111',
                'description': 'Lapangan futsal modern dengan fasilitas lengkap di pusat Jakarta. Lantai sintetis berkualitas tinggi, pencahayaan LED, dan AC.',
                'price_per_hour': Decimal('150000'),
                'number_of_courts': 3,
            },
            {
                'name': 'Champion Futsal Center',
                'category': 'FUTSAL',
                'owner': 'mitra_futsal_jakarta',
                'address': 'Jl. Kemang Raya No. 45, Jakarta Selatan, DKI Jakarta',
                'location_url': 'https://maps.google.com/champion-futsal',
                'contact': '+62812-1111-2222',
                'description': 'Futsal center dengan 4 lapangan berkualitas internasional. Dilengkapi kantin, parkir luas, dan ruang ganti.',
                'price_per_hour': Decimal('180000'),
                'number_of_courts': 4,
            },
            
            # Badminton venues
            {
                'name': 'Shuttle Court Bandung',
                'category': 'BADMINTON',
                'owner': 'mitra_badminton_bandung',
                'address': 'Jl. Dago No. 67, Bandung, Jawa Barat',
                'location_url': 'https://maps.google.com/shuttle-court-bandung',
                'contact': '+62812-2222-2222',
                'description': 'Lapangan badminton premium dengan karpet BWF standard. 8 lapangan indoor dengan AC dan pencahayaan profesional.',
                'price_per_hour': Decimal('80000'),
                'number_of_courts': 8,
            },
            {
                'name': 'Bandung Badminton Hall',
                'category': 'BADMINTON',
                'owner': 'mitra_badminton_bandung',
                'address': 'Jl. Pasteur No. 89, Bandung, Jawa Barat',
                'location_url': 'https://maps.google.com/badminton-hall-bandung',
                'contact': '+62812-2222-3333',
                'description': 'Hall badminton dengan 12 lapangan. Fasilitas lengkap termasuk cafe, pro shop, dan area spectator.',
                'price_per_hour': Decimal('75000'),
                'number_of_courts': 12,
            },
            
            # Basketball venues
            {
                'name': 'Surabaya Basketball Complex',
                'category': 'BASKET',
                'owner': 'mitra_basket_surabaya',
                'address': 'Jl. Ahmad Yani No. 234, Surabaya, Jawa Timur',
                'location_url': 'https://maps.google.com/basketball-surabaya',
                'contact': '+62812-3333-3333',
                'description': 'Kompleks basket outdoor dan indoor dengan standar internasional. Ring adjustable, lantai kayu parket.',
                'price_per_hour': Decimal('200000'),
                'number_of_courts': 2,
            },
            {
                'name': 'Urban Basketball Court',
                'category': 'BASKET',
                'owner': 'mitra_basket_surabaya',
                'address': 'Jl. Pemuda No. 156, Surabaya, Jawa Timur',
                'location_url': 'https://maps.google.com/urban-basketball',
                'contact': '+62812-3333-4444',
                'description': 'Lapangan basket urban style dengan suasana street basketball. Outdoor court dengan floodlight malam.',
                'price_per_hour': Decimal('120000'),
                'number_of_courts': 1,
            },
            
            # Tennis venues
            {
                'name': 'Yogya Tennis Club',
                'category': 'TENIS',
                'owner': 'mitra_tenis_yogya',
                'address': 'Jl. Malioboro No. 78, Yogyakarta, DIY',
                'location_url': 'https://maps.google.com/yogya-tennis',
                'contact': '+62812-4444-4444',
                'description': 'Klub tenis eksklusif dengan lapangan clay dan hard court. Fasilitas club house dan pelatih tersedia.',
                'price_per_hour': Decimal('100000'),
                'number_of_courts': 6,
            },
            
            # Volleyball venues
            {
                'name': 'Medan Volleyball Arena',
                'category': 'VOLI',
                'owner': 'mitra_voli_medan',
                'address': 'Jl. Gatot Subroto No. 45, Medan, Sumatera Utara',
                'location_url': 'https://maps.google.com/medan-volleyball',
                'contact': '+62812-5555-5555',
                'description': 'Arena voli indoor dengan net profesional dan lantai khusus voli. Kapasitas spectator 200 orang.',
                'price_per_hour': Decimal('130000'),
                'number_of_courts': 3,
            },
            
            # Additional venues for variety
            {
                'name': 'Elite Futsal Jakarta',
                'category': 'FUTSAL',
                'owner': 'mitra_futsal_jakarta',
                'address': 'Jl. Thamrin No. 90, Jakarta Pusat, DKI Jakarta',
                'location_url': 'https://maps.google.com/elite-futsal',
                'contact': '+62812-1111-5555',
                'description': 'Futsal premium dengan teknologi terbaru. Booking system digital, live streaming, dan virtual reality corner.',
                'price_per_hour': Decimal('220000'),
                'number_of_courts': 2,
            },
            {
                'name': 'Smash Badminton Bandung',
                'category': 'BADMINTON',
                'owner': 'mitra_badminton_bandung',
                'address': 'Jl. Setiabudhi No. 123, Bandung, Jawa Barat',
                'location_url': 'https://maps.google.com/smash-badminton',
                'contact': '+62812-2222-6666',
                'description': 'Lapangan badminton dengan kualitas tournament grade. Sistem ventilasi terbaik dan no-echo sound system.',
                'price_per_hour': Decimal('90000'),
                'number_of_courts': 6,
            },
        ]
        
        for venue_data in venues_data:
            # Resolve related objects but don't write fields that no longer
            # exist on Venue (category, price_per_hour were moved to Court)
            category_obj = SportsCategory.objects.get(name=venue_data['category'])
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

            # Keep mapping of venue -> seed info so we can create courts with
            # the right category and price later (Court now holds those fields)
            if not hasattr(self, '_venue_seed_info'):
                self._venue_seed_info = {}
            self._venue_seed_info[venue.name] = {
                'category': category_obj,
                'price_per_hour': venue_data['price_per_hour']
            }

        self.stdout.write(f'Created {Venue.objects.count()} venues')

    def download_and_save_image(self, url, filename):
        """Download image from URL and return ContentFile"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return ContentFile(response.content, filename)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Failed to download image: {e}'))
        return None

    def create_venue_images(self):
        """Create venue images using the provided URL"""
        self.stdout.write('Creating venue images...')
        
        image_url = 'https://cnc-magazine.oramiland.com/parenting/images/ukuran_lapangan_sepak_bola.width-800.format-webp.webp'
        
        venues = Venue.objects.all()
        
        for i, venue in enumerate(venues):
            # Create 2-4 images per venue
            num_images = random.randint(2, 4)
            
            for j in range(num_images):
                image_file = self.download_and_save_image(
                    image_url, 
                    f'venue_{venue.id}_{j+1}.webp'
                )
                
                if image_file:
                    venue_image = VenueImage.objects.create(
                        venue=venue,
                        image=image_file,
                        is_primary=(j == 0),  # First image is primary
                        caption=f'Lapangan {venue.name} - View {j+1}',
                    )

        self.stdout.write(f'Created {VenueImage.objects.count()} venue images')

    def create_venue_facilities(self):
        """Assign facilities to venues"""
        self.stdout.write('Creating venue facilities...')
        
        venues = Venue.objects.all()
        facilities = list(Facility.objects.all())
        
        for venue in venues:
            # Each venue gets 5-10 random facilities
            num_facilities = random.randint(5, 10)
            selected_facilities = random.sample(facilities, num_facilities)
            
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
        
        for venue in venues:
            seed_info = getattr(self, '_venue_seed_info', {}).get(venue.name, {})
            category = seed_info.get('category')
            price = seed_info.get('price_per_hour', Decimal('0'))

            for i in range(venue.number_of_courts):
                court_name = f"Court {i+1}" if venue.number_of_courts > 1 else "Main Court"
                
                Court.objects.get_or_create(
                    venue=venue,
                    name=court_name,
                    defaults={
                        'is_active': True,
                        'maintenance_notes': None if random.random() > 0.1 else 'Regular maintenance schedule',
                        'category': category,
                        'price_per_hour': price,
                        'description': venue.description,
                    }
                )

        self.stdout.write(f'Created {Court.objects.count()} courts')

    def create_operational_hours(self):
        """Create operational hours for venues"""
        self.stdout.write('Creating operational hours...')
        
        venues = Venue.objects.all()
        
        # Common operational patterns
        patterns = [
            # Pattern 1: 24/7 operation
            {'open': time(0, 0), 'close': time(23, 59), 'days': list(range(7))},
            # Pattern 2: 06:00 - 24:00
            {'open': time(6, 0), 'close': time(23, 59), 'days': list(range(7))},
            # Pattern 3: 08:00 - 22:00
            {'open': time(8, 0), 'close': time(22, 0), 'days': list(range(7))},
            # Pattern 4: 06:00 - 22:00 weekdays, 08:00 - 24:00 weekends
            {'open': time(6, 0), 'close': time(22, 0), 'days': [0, 1, 2, 3, 4]},
        ]
        
        for venue in venues:
            pattern = random.choice(patterns)
            
            for day in range(7):
                if day in pattern['days']:
                    # Weekend hours might be different
                    if day in [5, 6] and len(pattern['days']) == 5:  # Weekend
                        open_time = time(8, 0)
                        close_time = time(23, 59)
                    else:
                        open_time = pattern['open']
                        close_time = pattern['close']
                    
                    OperationalHour.objects.get_or_create(
                        venue=venue,
                        day_of_week=day,
                        defaults={
                            'open_time': open_time,
                            'close_time': close_time,
                            'is_closed': False,
                        }
                    )
                else:
                    # Closed day
                    OperationalHour.objects.get_or_create(
                        venue=venue,
                        day_of_week=day,
                        defaults={
                            'open_time': time(9, 0),
                            'close_time': time(17, 0),
                            'is_closed': True,
                        }
                    )

        self.stdout.write(f'Created {OperationalHour.objects.count()} operational hour entries')

    def create_bookings(self):
        """Create sample bookings"""
        self.stdout.write('Creating bookings...')
        
        users = list(User.objects.filter(role='user'))
        courts = list(Court.objects.all())
        
        # Create bookings for the past month and next 2 weeks
        start_date = date.today() - timedelta(days=30)
        end_date = date.today() + timedelta(days=14)
        
        booking_count = 0
        current_date = start_date
        
        while current_date <= end_date and booking_count < 100:  # Limit to 100 bookings
            # Random chance of having bookings on any given day
            if random.random() < 0.7:  # 70% chance of bookings per day
                daily_bookings = random.randint(1, 5)
                
                for _ in range(daily_bookings):
                    user = random.choice(users)
                    court = random.choice(courts)
                    
                    # Random start time between 6 AM and 10 PM
                    start_hour = random.randint(6, 22)
                    start_time = time(start_hour, random.choice([0, 30]))
                    
                    # Random duration 1-3 hours
                    duration = random.choice([1, 1.5, 2, 2.5, 3])
                    end_hour = start_hour + int(duration)
                    end_minute = start_time.minute + int((duration % 1) * 60)
                    
                    if end_minute >= 60:
                        end_hour += 1
                        end_minute -= 60
                    
                    if end_hour < 24:  # Valid time
                        end_time = time(end_hour, end_minute)
                        # price is stored on Court now
                        total_price = court.price_per_hour * Decimal(str(duration))
                        
                        # Determine status based on date
                        if current_date < date.today():
                            status = random.choices(
                                ['completed', 'cancelled'],
                                weights=[0.8, 0.2]
                            )[0]
                        elif current_date == date.today():
                            status = random.choices(
                                ['confirmed', 'pending'],
                                weights=[0.7, 0.3]
                            )[0]
                        else:
                            status = random.choices(
                                ['confirmed', 'pending'],
                                weights=[0.6, 0.4]
                            )[0]
                        
                        payment_status = 'paid' if status in ['completed', 'confirmed'] else 'unpaid'
                        
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
                                notes=random.choice([
                                    None, 
                                    'Tournament practice',
                                    'Company event',
                                    'Birthday celebration',
                                    'Regular weekly session'
                                ])
                            )
                            booking_count += 1
                        except Exception:
                            # Skip if there's a conflict
                            pass
            
            current_date += timedelta(days=1)

        self.stdout.write(f'Created {Booking.objects.count()} bookings')

    def create_payments(self):
        """Create payments for bookings"""
        self.stdout.write('Creating payments...')
        
        paid_bookings = Booking.objects.filter(payment_status='paid')
        
        payment_methods = ['bank_transfer', 'e_wallet', 'credit_card', 'cash']
        admin = User.objects.filter(role='admin').first()
        
        for booking in paid_bookings:
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                payment_method=random.choice(payment_methods),
                transaction_id=f'TXN{random.randint(100000, 999999)}',
                verified_by=admin if random.random() > 0.2 else None,  # 80% verified
                notes=random.choice([
                    None,
                    'Payment verified',
                    'Manual verification required',
                    'Auto payment processing'
                ]),
                paid_at=booking.created_at + timedelta(minutes=random.randint(1, 60))
            )

        self.stdout.write(f'Created {Payment.objects.count()} payments')

    def create_reviews(self):
        """Create reviews for completed bookings"""
        self.stdout.write('Creating reviews...')
        
        completed_bookings = Booking.objects.filter(booking_status='completed')
        
        review_comments = [
            "Lapangan bagus, fasilitas lengkap. Recommended!",
            "Pelayanan memuaskan, lapangan bersih dan terawat.",
            "Lokasi strategis, parkir luas. Akan booking lagi.",
            "Fasilitas OK, tapi bisa ditingkatkan lagi kebersihan toilet.",
            "Lapangan berkualitas, harga sesuai dengan fasilitas.",
            "Sempurna untuk main bareng teman-teman!",
            "Lapangan standar internasional, sangat puas.",
            "Good experience, staff friendly dan helpful.",
            "Lapangan agak sempit, tapi overall OK lah.",
            "Excellent venue! Highly recommended untuk turnamen.",
        ]
        
        # About 60% of completed bookings have reviews
        reviewed_bookings = random.sample(
            list(completed_bookings), 
            int(len(completed_bookings) * 0.6)
        )
        
        for booking in reviewed_bookings:
            rating = random.choices(
                [1, 2, 3, 4, 5],
                weights=[0.05, 0.05, 0.15, 0.35, 0.4]  # Mostly positive reviews
            )[0]
            
            comment = random.choice(review_comments) if random.random() > 0.2 else None
            
            Review.objects.create(
                booking=booking,
                rating=rating,
                comment=comment,
                created_at=booking.created_at + timedelta(
                    days=random.randint(1, 7)
                )
            )

        self.stdout.write(f'Created {Review.objects.count()} reviews')

    def create_activity_logs(self):
        """Create activity logs for user actions"""
        self.stdout.write('Creating activity logs...')
        
        users = list(User.objects.all())
        actions = ['login', 'logout', 'booking', 'payment', 'update', 'create']
        
        # Create logs for the past 30 days
        start_date = timezone.now() - timedelta(days=30)
        
        for _ in range(200):  # Create 200 activity logs
            user = random.choice(users)
            action = random.choice(actions)
            
            # Generate realistic descriptions based on action
            descriptions = {
                'login': f'User {user.username} logged in successfully',
                'logout': f'User {user.username} logged out',
                'booking': f'User {user.username} created a new booking',
                'payment': f'User {user.username} completed payment',
                'update': f'User {user.username} updated profile information',
                'create': f'User {user.username} created new venue' if user.role == 'mitra' else f'User {user.username} registered account',
            }
            
            ActivityLog.objects.create(
                user=user,
                action_type=action,
                description=descriptions[action],
                ip_address=f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
                user_agent='Mozilla/5.0 (compatible; LapangIN/1.0)',
                timestamp=start_date + timedelta(
                    seconds=random.randint(0, int((timezone.now() - start_date).total_seconds()))
                )
            )

        self.stdout.write(f'Created {ActivityLog.objects.count()} activity logs')