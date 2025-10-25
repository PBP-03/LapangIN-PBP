from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
import json
import os
from datetime import datetime, time, date, timedelta

# Import from new apps
from app.users.models import User
from app.venues.models import SportsCategory, Venue, VenueImage, Facility, VenueFacility, OperationalHour
from app.courts.models import Court, CourtSession, CourtImage
from app.bookings.models import Booking, Payment
from app.reviews.models import Review
from app.revenue.models import ActivityLog, Pendapatan

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with venue data from data.json and generate additional realistic data'

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

        self.stdout.write(self.style.SUCCESS('Starting data seeding from JSON...'))
        
        # Load the JSON data
        self.load_json_data()
        
        # Create data in order of dependencies
        self.create_users()
        self.create_sports_categories()
        self.create_facilities()
        self.create_venues_from_json()
        self.create_venue_images()
        self.create_venue_facilities()
        self.create_courts()
        self.create_court_sessions()
        self.create_court_images()
        self.create_operational_hours()
        self.create_bookings()
        self.create_payments()
        self.create_reviews()
        self.create_pendapatan()
        self.create_activity_logs()
        
        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))

    def load_json_data(self):
        """Load venue data from data.json"""
        # Get the project root directory (5 levels up from this file)
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 'static', 'dataset', 'data.json')
        
        with open(json_path, 'r', encoding='utf-8') as file:
            self.venue_data = json.load(file)
        
        self.stdout.write(f'Loaded {len(self.venue_data)} venues from JSON file')

    def clear_data(self):
        """Clear all existing data"""
        models_to_clear = [
            ActivityLog, Pendapatan, Review, Payment, Booking, OperationalHour,
            CourtImage, CourtSession, Court, VenueFacility, VenueImage, Venue, Facility,
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

        # Create mitra users based on unique categories from JSON
        categories_in_data = list(set([venue['Category'] for venue in self.venue_data]))
        
        mitra_templates = [
            {'name': 'Ahmad', 'surname': 'Futsal', 'location': 'Jakarta'},
            {'name': 'Sari', 'surname': 'Badminton', 'location': 'Bandung'},
            {'name': 'Budi', 'surname': 'Basketball', 'location': 'Surabaya'},
            {'name': 'Diana', 'surname': 'Tennis', 'location': 'Yogyakarta'},
            {'name': 'Rizki', 'surname': 'Volleyball', 'location': 'Medan'},
            {'name': 'Andi', 'surname': 'Sports', 'location': 'Bogor'},
            {'name': 'Maya', 'surname': 'Arena', 'location': 'Depok'},
            {'name': 'Joko', 'surname': 'Center', 'location': 'Tangerang'},
            {'name': 'Siska', 'surname': 'Hall', 'location': 'Bekasi'},
            {'name': 'Dedi', 'surname': 'Club', 'location': 'Malang'},
        ]

        # Create enough mitras for the venues
        for i, template in enumerate(mitra_templates):
            user, created = User.objects.get_or_create(
                username=f'mitra_{template["name"].lower()}_{i+1}',
                defaults={
                    'email': f'{template["name"].lower()}.{template["surname"].lower()}@lapangin.com',
                    'first_name': template['name'],
                    'last_name': template['surname'],
                    'phone_number': f'+62812-{1111+i:04d}-{1111+i:04d}',
                    'address': f'{template["location"]}, Indonesia',
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
            {
                'username': 'lisa_anderson',
                'email': 'lisa.anderson@email.com',
                'first_name': 'Lisa',
                'last_name': 'Anderson',
                'phone_number': '+62812-1234-5678',
                'address': 'Bogor, Jawa Barat',
            },
            {
                'username': 'tommy_wijaya',
                'email': 'tommy.wijaya@email.com',
                'first_name': 'Tommy',
                'last_name': 'Wijaya',
                'phone_number': '+62812-2345-6789',
                'address': 'Tangerang, Banten',
            },
            {
                'username': 'maria_sari',
                'email': 'maria.sari@email.com',
                'first_name': 'Maria',
                'last_name': 'Sari',
                'phone_number': '+62812-3456-7890',
                'address': 'Depok, Jawa Barat',
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
        """Create sports categories based on JSON data"""
        self.stdout.write('Creating sports categories...')
        
        # Get unique categories from JSON and create descriptions
        category_descriptions = {
            'FUTSAL': 'Olahraga futsal dengan lapangan indoor berukuran standar FIFA',
            'BADMINTON': 'Olahraga badminton dengan lapangan indoor dan net standar BWF',
            'BASKET': 'Olahraga basket dengan lapangan indoor/outdoor berstandar internasional',
            'TENNIS': 'Olahraga tenis dengan lapangan outdoor/indoor surface berkualitas',
            'PADEL': 'Olahraga padel dengan lapangan khusus berdinding kaca',
            'VOLI': 'Olahraga voli dengan lapangan indoor/outdoor dan net profesional',
        }
        
        # Create categories from JSON data
        categories_in_data = set([venue['Category'] for venue in self.venue_data])
        
        for category_name in categories_in_data:
            description = category_descriptions.get(category_name, f'Olahraga {category_name.lower()}')
            category, created = SportsCategory.objects.get_or_create(
                name=category_name,
                defaults={'description': description}
            )

        self.stdout.write(f'Created {SportsCategory.objects.count()} sports categories')

    def create_facilities(self):
        """Create facility types based on JSON data"""
        self.stdout.write('Creating facilities...')
        
        # Extract all unique facilities from JSON data
        all_facilities = set()
        for venue in self.venue_data:
            if 'Facilities' in venue and venue['Facilities']:
                all_facilities.update(venue['Facilities'])
        
        # Create additional common facilities not in JSON
        additional_facilities = [
            'CCTV',
            'Penjaga Lapangan',
            'Loker',
            'First Aid Kit',
            'Sound System',
            'Pencahayaan LED',
            'Area Istirahat',
            'Lapangan Berkualitas Sintetis',
        ]
        
        all_facilities.update(additional_facilities)
        
        for facility_name in all_facilities:
            facility, created = Facility.objects.get_or_create(
                name=facility_name,
                defaults={'description': f'Fasilitas {facility_name} tersedia di venue'}
            )

        self.stdout.write(f'Created {Facility.objects.count()} facilities')

    def create_venues_from_json(self):
        """Create venues using data from JSON file"""
        self.stdout.write('Creating venues from JSON data...')
        
        admin = User.objects.filter(role='admin').first()
        mitras = list(User.objects.filter(role='mitra'))
        
        for i, venue_data in enumerate(self.venue_data):
            # Assign a random mitra as owner
            owner = mitras[i % len(mitras)]
            
            # Clean up the venue name and create a description
            venue_name = venue_data['name'].strip()
            
            # Generate description based on venue data
            description = self.generate_venue_description(venue_data)
            
            # Handle contact field - could be null, string, or phone number
            contact = venue_data.get('Contact')
            if contact and not str(contact).startswith('+'):
                if str(contact).startswith('08'):
                    contact = '+62' + str(contact)[1:]  # Convert Indonesian format
                elif str(contact).startswith('62'):
                    contact = '+' + str(contact)
                elif contact == 'null' or contact == '':
                    contact = None
            
            venue, created = Venue.objects.get_or_create(
                name=venue_name,
                defaults={
                    'owner': owner,
                    'address': venue_data['address'],
                    'location_url': venue_data.get('location', ''),
                    'contact': contact,
                    'description': description,
                    'number_of_courts': venue_data.get('jumlahLapangan', 1),
                    'verification_status': 'approved',
                    'verified_by': admin,
                    'verification_date': timezone.now(),
                }
            )

            # Store venue info for later use in courts
            if not hasattr(self, '_venue_seed_info'):
                self._venue_seed_info = {}
            
            self._venue_seed_info[venue.name] = {
                'category': venue_data['Category'],
                'price_per_hour': Decimal(str(venue_data.get('Price', 100000))),
                'facilities': venue_data.get('Facilities', []),
                'operational_hours': venue_data.get('OperationalHours', []),
                'images': venue_data.get('Image', []),
            }

        self.stdout.write(f'Created {Venue.objects.count()} venues from JSON data')

    def generate_venue_description(self, venue_data):
        """Generate a realistic description for the venue"""
        category = venue_data['Category'].lower()
        court_count = venue_data.get('jumlahLapangan', 1)
        facilities = venue_data.get('Facilities', [])
        
        description_templates = {
            'futsal': f"Lapangan futsal modern dengan {court_count} lapangan berkualitas tinggi. ",
            'badminton': f"Hall badminton premium dengan {court_count} lapangan standar BWF. ",
            'basket': f"Lapangan basket berkualitas internasional dengan {court_count} lapangan. ",
            'tennis': f"Lapangan tenis dengan {court_count} court berkualitas tinggi. ",
            'padel': f"Arena padel modern dengan {court_count} lapangan standar internasional. ",
            'voli': f"Lapangan voli profesional dengan {court_count} lapangan berstandar. ",
        }
        
        base_description = description_templates.get(category, f"Venue olahraga {category} dengan {court_count} lapangan. ")
        
        # Add facility highlights
        premium_facilities = ['Cafe & Resto', 'Hot Shower', 'Wi-Fi', 'AC', 'Tribun Penonton']
        venue_premium_facilities = [f for f in facilities if f in premium_facilities]
        
        if venue_premium_facilities:
            base_description += f"Dilengkapi dengan fasilitas premium seperti {', '.join(venue_premium_facilities[:3])}. "
        
        base_description += "Lokasi strategis dengan akses mudah dan parkir luas. Cocok untuk latihan rutin, turnamen, dan acara olahraga."
        
        return base_description

    def create_venue_images(self):
        """Create venue images using data from JSON and dataset photos"""
        self.stdout.write('Creating venue images...')
        
        venues = Venue.objects.all()
        
        for venue in venues:
            seed_info = self._venue_seed_info.get(venue.name, {})
            image_files = seed_info.get('images', [])
            
            # Use the images from JSON data
            for i, image_file in enumerate(image_files):
                # Convert to static URL path
                image_url = f'/static/img/dataset-photos/{image_file}'
                
                VenueImage.objects.create(
                    venue=venue,
                    image_url=image_url,
                    is_primary=(i == 0),  # First image is primary
                    caption=f'{venue.name} - View {i+1}',
                )
            
            # If no images in JSON, create some default ones
            if not image_files:
                default_image_url = '/static/img/dataset-photos/default-venue.jpg'
                VenueImage.objects.create(
                    venue=venue,
                    image_url=default_image_url,
                    is_primary=True,
                    caption=f'{venue.name} - Main View',
                )

        self.stdout.write(f'Created {VenueImage.objects.count()} venue images')

    def create_venue_facilities(self):
        """Assign facilities to venues based on JSON data"""
        self.stdout.write('Creating venue facilities...')
        
        venues = Venue.objects.all()
        
        for venue in venues:
            seed_info = self._venue_seed_info.get(venue.name, {})
            facility_names = seed_info.get('facilities', [])
            
            for facility_name in facility_names:
                try:
                    facility = Facility.objects.get(name=facility_name)
                    VenueFacility.objects.get_or_create(
                        venue=venue,
                        facility=facility
                    )
                except Facility.DoesNotExist:
                    # Create facility if it doesn't exist
                    facility = Facility.objects.create(
                        name=facility_name,
                        description=f'Fasilitas {facility_name}'
                    )
                    VenueFacility.objects.create(venue=venue, facility=facility)

        self.stdout.write(f'Created {VenueFacility.objects.count()} venue-facility relationships')

    def create_courts(self):
        """Create individual courts for each venue"""
        self.stdout.write('Creating courts...')
        
        venues = Venue.objects.all()
        
        for venue in venues:
            seed_info = self._venue_seed_info.get(venue.name, {})
            category_name = seed_info.get('category', 'FUTSAL')
            price = seed_info.get('price_per_hour', Decimal('100000'))
            
            try:
                category = SportsCategory.objects.get(name=category_name)
            except SportsCategory.DoesNotExist:
                category = SportsCategory.objects.first()  # fallback

            for i in range(venue.number_of_courts):
                court_name = f"Court {i+1}" if venue.number_of_courts > 1 else "Main Court"
                
                Court.objects.get_or_create(
                    venue=venue,
                    name=court_name,
                    defaults={
                        'category': category,
                        'price_per_hour': price,
                        'is_active': True,
                        'description': venue.description,
                        'maintenance_notes': None if random.random() > 0.1 else 'Regular maintenance schedule',
                    }
                )

        self.stdout.write(f'Created {Court.objects.count()} courts')

    def create_court_sessions(self):
        """Create time slot sessions for courts"""
        self.stdout.write('Creating court sessions...')
        
        courts = Court.objects.all()
        
        # Different session patterns based on sport type
        session_patterns = {
            'FUTSAL': [
                {'name': f'Session {i+1}', 'start': time(6 + i, 0), 'end': time(7 + i, 0)}
                for i in range(17)  # 6 AM to 11 PM
            ],
            'BADMINTON': [
                {'name': f'Session {i+1}', 'start': time(6 + i, 0), 'end': time(7 + i, 0)}
                for i in range(17)  # 6 AM to 11 PM
            ],
            'BASKET': [
                {'name': 'Morning', 'start': time(6, 0), 'end': time(10, 0)},
                {'name': 'Afternoon', 'start': time(10, 0), 'end': time(14, 0)},
                {'name': 'Evening', 'start': time(14, 0), 'end': time(18, 0)},
                {'name': 'Night', 'start': time(18, 0), 'end': time(22, 0)},
            ],
            'TENNIS': [
                {'name': f'Session {i+1}', 'start': time(6 + i, 0), 'end': time(8 + i, 0)}
                for i in range(8)  # 2-hour blocks
            ],
            'PADEL': [
                {'name': f'Session {i+1}', 'start': time(6 + i*2, 0), 'end': time(8 + i*2, 0)}
                for i in range(8)  # 2-hour blocks
            ],
        }
        
        for court in courts:
            # Choose pattern based on court category
            category_name = court.category.name if court.category else 'FUTSAL'
            pattern = session_patterns.get(category_name, session_patterns['FUTSAL'])
            
            for session_data in pattern:
                CourtSession.objects.get_or_create(
                    court=court,
                    start_time=session_data['start'],
                    defaults={
                        'session_name': session_data['name'],
                        'end_time': session_data['end'],
                        'is_active': True,
                    }
                )
        
        self.stdout.write(f'Created {CourtSession.objects.count()} court sessions')

    def create_court_images(self):
        """Create images for individual courts"""
        self.stdout.write('Creating court images...')
        
        courts = Court.objects.all()
        
        for court in courts:
            # Use venue images as court images
            venue_images = VenueImage.objects.filter(venue=court.venue)
            
            for i, venue_image in enumerate(venue_images[:2]):  # Max 2 images per court
                CourtImage.objects.create(
                    court=court,
                    image_url=venue_image.image_url,
                    is_primary=(i == 0),
                    caption=f'{court.name} - View {i+1}',
                )
            
            # If no venue images, create default
            if not venue_images.exists():
                CourtImage.objects.create(
                    court=court,
                    image_url='/static/img/dataset-photos/default-court.jpg',
                    is_primary=True,
                    caption=f'{court.name} - Main View',
                )
        
        self.stdout.write(f'Created {CourtImage.objects.count()} court images')

    def create_operational_hours(self):
        """Create operational hours based on JSON data"""
        self.stdout.write('Creating operational hours...')
        
        venues = Venue.objects.all()
        
        for venue in venues:
            seed_info = self._venue_seed_info.get(venue.name, {})
            operational_hours = seed_info.get('operational_hours', [])
            
            # Parse operational hours from JSON (format: "HH.MM - HH.MM")
            if operational_hours and len(operational_hours) == 7:
                for day_index, hour_string in enumerate(operational_hours):
                    if hour_string and ' - ' in hour_string:
                        try:
                            open_str, close_str = hour_string.split(' - ')
                            open_time = self.parse_time_string(open_str)
                            close_time = self.parse_time_string(close_str)
                            
                            OperationalHour.objects.get_or_create(
                                venue=venue,
                                day_of_week=day_index,
                                defaults={
                                    'open_time': open_time,
                                    'close_time': close_time,
                                    'is_closed': False,
                                }
                            )
                        except:
                            # Fallback to default hours
                            self.create_default_operational_hours(venue, day_index)
                    else:
                        self.create_default_operational_hours(venue, day_index)
            else:
                # Create default operational hours for all days
                for day_index in range(7):
                    self.create_default_operational_hours(venue, day_index)

        self.stdout.write(f'Created {OperationalHour.objects.count()} operational hour entries')

    def parse_time_string(self, time_str):
        """Parse time string in format 'HH.MM' to time object"""
        if time_str == "00.00":
            return time(0, 0)
        elif time_str == "24.00":
            return time(23, 59)
        else:
            hour, minute = time_str.split('.')
            return time(int(hour), int(minute))

    def create_default_operational_hours(self, venue, day_index):
        """Create default operational hours for a venue and day"""
        OperationalHour.objects.get_or_create(
            venue=venue,
            day_of_week=day_index,
            defaults={
                'open_time': time(6, 0),
                'close_time': time(23, 0),
                'is_closed': False,
            }
        )

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
        
        while current_date <= end_date and booking_count < 150:  # Limit to 150 bookings
            # Random chance of having bookings on any given day
            if random.random() < 0.7:  # 70% chance of bookings per day
                daily_bookings = random.randint(1, 8)
                
                for _ in range(daily_bookings):
                    user = random.choice(users)
                    court = random.choice(courts)
                    
                    # Random start time between 6 AM and 9 PM
                    start_hour = random.randint(6, 21)
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
                        total_price = court.price_per_hour * Decimal(str(duration))
                        
                        # Determine status based on date
                        if current_date < date.today():
                            status = random.choices(
                                ['completed', 'cancelled'],
                                weights=[0.85, 0.15]
                            )[0]
                        elif current_date == date.today():
                            status = random.choices(
                                ['confirmed', 'pending'],
                                weights=[0.8, 0.2]
                            )[0]
                        else:
                            status = random.choices(
                                ['confirmed', 'pending'],
                                weights=[0.7, 0.3]
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
                                    'Company team building',
                                    'Birthday celebration',
                                    'Regular weekly session',
                                    'Training session',
                                    'League match'
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
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': booking.total_price,
                    'payment_method': random.choice(payment_methods),
                    'transaction_id': f'TXN{random.randint(100000, 999999)}',
                    'verified_by': admin if random.random() > 0.15 else None,  # 85% verified
                    'notes': random.choice([
                        None,
                        'Payment verified automatically',
                        'Manual verification completed',
                        'Auto payment processing',
                        'Payment confirmed by admin'
                    ]),
                    'paid_at': booking.created_at + timedelta(minutes=random.randint(1, 60))
                }
            )

        self.stdout.write(f'Created {Payment.objects.count()} payments')

    def create_reviews(self):
        """Create reviews for completed bookings"""
        self.stdout.write('Creating reviews...')
        
        completed_bookings = Booking.objects.filter(booking_status='completed')
        
        review_comments = [
            "Lapangan bagus banget, fasilitas lengkap. Highly recommended!",
            "Pelayanan memuaskan, lapangan bersih dan terawat dengan baik.",
            "Lokasi strategis, parkir luas. Pasti booking lagi next time.",
            "Fasilitas OK, tapi bisa ditingkatkan lagi kebersihan toiletnya.",
            "Lapangan berkualitas tinggi, harga sesuai dengan fasilitas yang ada.",
            "Perfect venue untuk main bareng team! Lapangan mantap.",
            "Lapangan standar internasional, sangat puas dengan kualitasnya.",
            "Good experience overall, staff friendly dan sangat helpful.",
            "Lapangan agak sempit untuk ukuran turnamen, tapi overall masih OK.",
            "Excellent venue! Highly recommended untuk event dan turnamen.",
            "Tempatnya bersih, fasilitasnya lengkap, recommended banget!",
            "Harga agak mahal tapi sebanding dengan kualitas lapangan.",
            "Staff ramah, booking mudah, lapangan sesuai ekspektasi.",
            "Venue terbaik di area ini, selalu jadi pilihan utama.",
            "Fasilitas shower dan ruang ganti sangat bersih dan nyaman."
        ]
        
        # About 65% of completed bookings have reviews
        reviewed_bookings = random.sample(
            list(completed_bookings), 
            int(len(completed_bookings) * 0.65)
        )
        
        for booking in reviewed_bookings:
            rating = random.choices(
                [1, 2, 3, 4, 5],
                weights=[0.03, 0.07, 0.15, 0.35, 0.4]  # Mostly positive reviews
            )[0]
            
            comment = random.choice(review_comments) if random.random() > 0.25 else None
            
            Review.objects.create(
                booking=booking,
                rating=rating,
                comment=comment,
                created_at=booking.created_at + timedelta(
                    days=random.randint(1, 7)
                )
            )

        self.stdout.write(f'Created {Review.objects.count()} reviews')

    def create_pendapatan(self):
        """Create revenue/pendapatan entries for paid bookings"""
        self.stdout.write('Creating pendapatan records...')
        
        paid_bookings = Booking.objects.filter(payment_status='paid')
        
        for booking in paid_bookings:
            mitra = booking.court.venue.owner
            
            if mitra.role != 'mitra':
                continue
            
            # Commission rate varies between 5% to 15%
            commission_rate = Decimal(str(random.choice([5.00, 7.50, 10.00, 12.50, 15.00])))
            
            # Determine payment status based on booking date
            if booking.booking_date < date.today() - timedelta(days=14):
                payment_status = 'paid'
                paid_at = booking.created_at + timedelta(days=random.randint(7, 14))
            elif booking.booking_date < date.today():
                payment_status = random.choice(['paid', 'pending'])
                paid_at = booking.created_at + timedelta(days=random.randint(7, 14)) if payment_status == 'paid' else None
            else:
                payment_status = 'pending'
                paid_at = None
            
            pendapatan, created = Pendapatan.objects.get_or_create(
                booking=booking,
                defaults={
                    'mitra': mitra,
                    'amount': booking.total_price,
                    'commission_rate': commission_rate,
                    'payment_status': payment_status,
                    'paid_at': paid_at,
                    'notes': random.choice([
                        None,
                        'Commission processed successfully',
                        'Payment verified and transferred to mitra',
                        'Standard commission rate applied',
                        'Special rate for premium venue',
                        'Payment processed automatically'
                    ])
                }
            )
        
        self.stdout.write(f'Created {Pendapatan.objects.count()} pendapatan records')

    def create_activity_logs(self):
        """Create activity logs for user actions"""
        self.stdout.write('Creating activity logs...')
        
        users = list(User.objects.all())
        actions = ['login', 'logout', 'booking', 'payment', 'update', 'create', 'view']
        
        # Create logs for the past 30 days
        start_date = timezone.now() - timedelta(days=30)
        
        for _ in range(300):  # Create 300 activity logs
            user = random.choice(users)
            action = random.choice(actions)
            
            # Generate realistic descriptions based on action
            descriptions = {
                'login': f'User {user.username} logged in successfully',
                'logout': f'User {user.username} logged out',
                'booking': f'User {user.username} created a new booking',
                'payment': f'User {user.username} completed payment transaction',
                'update': f'User {user.username} updated profile information',
                'create': f'User {user.username} created new venue' if user.role == 'mitra' else f'User {user.username} registered account',
                'view': f'User {user.username} viewed venue details',
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