from django.core.management.base import BaseCommand
from app.venues.models import VenueImage
from app.courts.models import CourtImage


class Command(BaseCommand):
    help = 'Fix image paths from /static/dataset/images/ to /static/img/dataset-photos/'

    def handle(self, *args, **kwargs):
        # Fix venue images
        venue_images = VenueImage.objects.filter(image_url__startswith='/static/dataset/images/')
        venue_count = 0
        
        for img in venue_images:
            old_path = img.image_url
            # Replace /static/dataset/images/ with /static/img/dataset-photos/
            img.image_url = old_path.replace('/static/dataset/images/', '/static/img/dataset-photos/')
            img.save()
            venue_count += 1
        
        # Fix court images
        court_images = CourtImage.objects.filter(image_url__startswith='/static/dataset/images/')
        court_count = 0
        
        for img in court_images:
            old_path = img.image_url
            # Replace /static/dataset/images/ with /static/img/dataset-photos/
            img.image_url = old_path.replace('/static/dataset/images/', '/static/img/dataset-photos/')
            img.save()
            court_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted!\n'
                f'Venue images fixed: {venue_count}\n'
                f'Court images fixed: {court_count}\n'
                f'Total images fixed: {venue_count + court_count}'
            )
        )
