import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import time
from app.venues.models import Venue, VenueImage, Facility, VenueFacility, OperationalHour, SportsCategory
from app.courts.models import Court
from app.users.models import User


class Command(BaseCommand):
    help = 'Seeds venues, courts, and related data from data.json'

    def handle(self, *args, **kwargs):
        # Path to the JSON file
        json_path = os.path.join(settings.BASE_DIR, 'static', 'dataset', 'data.json')
        
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'JSON file not found at {json_path}'))
            return
        
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            venues_data = json.load(f)
        
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(venues_data)} venues from JSON'))
        
        # Create or get a default mitra user for venues
        mitra_user, created = User.objects.get_or_create(
            username='mitra_admin',
            defaults={
                'email': 'mitra@lapangin.com',
                'first_name': 'Mitra',
                'last_name': 'Admin',
                'role': 'mitra',
                'is_verified': True,
            }
        )
        if created:
            mitra_user.set_password('mitra123')
            mitra_user.save()
            self.stdout.write(self.style.SUCCESS('Created default mitra user: mitra_admin'))
        
        # Create or get admin user for verification
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@lapangin.com',
                'first_name': 'Admin',
                'last_name': 'LapangIN',
                'role': 'admin',
                'is_verified': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user: admin'))
        
        # Category mapping: JSON -> Django model
        category_mapping = {
            'BADMINTON': 'BADMINTON',
            'BASKET': 'BASKET',
            'FUTSAL': 'FUTSAL',
            'TENNIS': 'TENIS',
            'PADEL': 'PADEL',
        }
        
        # Ensure all sports categories exist
        for category_code in category_mapping.values():
            SportsCategory.objects.get_or_create(
                name=category_code,
                defaults={'description': f'{category_code} sports category'}
            )
        
        venues_created = 0
        venues_updated = 0
        
        for venue_data in venues_data:
            try:
                venue_name = venue_data.get('name')
                if not venue_name:
                    self.stdout.write(self.style.WARNING('Skipping venue with no name'))
                    continue
                
                # Get or create venue
                venue, created = Venue.objects.get_or_create(
                    name=venue_name,
                    defaults={
                        'owner': mitra_user,
                        'address': venue_data.get('address', ''),
                        'location_url': venue_data.get('location', ''),
                        'contact': venue_data.get('Contact', ''),
                        'number_of_courts': venue_data.get('jumlahLapangan', 1),
                        'verification_status': 'approved',
                        'verified_by': admin_user,
                        'verification_date': timezone.now(),
                    }
                )
                
                if created:
                    venues_created += 1
                    self.stdout.write(self.style.SUCCESS(f'Created venue: {venue_name}'))
                else:
                    venues_updated += 1
                    # Update existing venue
                    venue.address = venue_data.get('address', venue.address)
                    venue.location_url = venue_data.get('location', venue.location_url)
                    venue.contact = venue_data.get('Contact', venue.contact)
                    venue.number_of_courts = venue_data.get('jumlahLapangan', venue.number_of_courts)
                    venue.save()
                    self.stdout.write(self.style.WARNING(f'Updated venue: {venue_name}'))
                
                # Add venue images
                images = venue_data.get('Image', [])
                for idx, image_name in enumerate(images):
                    image_url = f'/static/img/dataset-photos/{image_name}'
                    VenueImage.objects.get_or_create(
                        venue=venue,
                        image_url=image_url,
                        defaults={
                            'is_primary': idx == 0,  # First image is primary
                            'caption': f'{venue_name} - Image {idx + 1}'
                        }
                    )
                
                # Add facilities
                facilities = venue_data.get('Facilities', [])
                for facility_name in facilities:
                    facility, _ = Facility.objects.get_or_create(
                        name=facility_name,
                        defaults={'description': f'{facility_name} facility'}
                    )
                    VenueFacility.objects.get_or_create(
                        venue=venue,
                        facility=facility
                    )
                
                # Add operational hours
                operational_hours = venue_data.get('OperationalHours', [])
                for day_index, hours_str in enumerate(operational_hours):
                    if not hours_str or hours_str == "":
                        continue
                    
                    # Parse hours like "08.00 - 23.00" or "00.00 - 24.00"
                    try:
                        open_str, close_str = hours_str.split(' - ')
                        open_hour, open_min = map(int, open_str.split('.'))
                        close_hour, close_min = map(int, close_str.split('.'))
                        
                        # Handle 24.00 as 23:59
                        if close_hour == 24:
                            close_hour = 23
                            close_min = 59
                        
                        open_time_obj = time(hour=open_hour, minute=open_min)
                        close_time_obj = time(hour=close_hour, minute=close_min)
                        
                        OperationalHour.objects.get_or_create(
                            venue=venue,
                            day_of_week=day_index,
                            defaults={
                                'open_time': open_time_obj,
                                'close_time': close_time_obj,
                                'is_closed': False
                            }
                        )
                    except (ValueError, IndexError) as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Could not parse operational hours for {venue_name} day {day_index}: {hours_str} - {e}'
                            )
                        )
                
                # Create courts based on category
                category_name = venue_data.get('Category', '').upper()
                mapped_category = category_mapping.get(category_name)
                
                if mapped_category:
                    sports_category = SportsCategory.objects.get(name=mapped_category)
                    price = venue_data.get('Price', 0)
                    
                    # Get venue images to use for courts
                    venue_images = venue_data.get('Image', [])
                    
                    # Create courts based on number_of_courts
                    for court_num in range(1, venue.number_of_courts + 1):
                        court, court_created = Court.objects.get_or_create(
                            venue=venue,
                            name=f'Court {court_num}',
                            defaults={
                                'category': sports_category,
                                'price_per_hour': price,
                                'is_active': True,
                            }
                        )
                        
                        # Add court images (use venue images since we don't have separate court images)
                        if venue_images and court_created:
                            from app.courts.models import CourtImage
                            # Use the first venue image for this court, or cycle through if multiple courts
                            image_index = (court_num - 1) % len(venue_images)
                            image_name = venue_images[image_index]
                            image_url = f'/static/img/dataset-photos/{image_name}'
                            
                            CourtImage.objects.get_or_create(
                                court=court,
                                image_url=image_url,
                                defaults={
                                    'is_primary': True,
                                    'caption': f'{court.name} - {venue_name}'
                                }
                            )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing venue {venue_data.get("name", "unknown")}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding completed!\n'
                f'Venues created: {venues_created}\n'
                f'Venues updated: {venues_updated}\n'
                f'Total venues: {Venue.objects.count()}\n'
                f'Total courts: {Court.objects.count()}\n'
                f'Total facilities: {Facility.objects.count()}'
            )
        )
