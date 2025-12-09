from django.core.management.base import BaseCommand
from app.courts.models import Court, CourtImage
from app.venues.models import VenueImage


class Command(BaseCommand):
    help = 'Add images to courts using their venue images'

    def handle(self, *args, **kwargs):
        courts = Court.objects.all()
        added = 0
        skipped = 0
        
        for court in courts:
            # Check if court already has images
            if court.images.exists():
                skipped += 1
                continue
            
            # Get venue images
            venue_images = VenueImage.objects.filter(venue=court.venue)
            
            if venue_images.exists():
                # Use the first venue image for the court
                img = venue_images.first()
                CourtImage.objects.create(
                    court=court,
                    image_url=img.image_url,
                    is_primary=True,
                    caption=f'{court.name} - {court.venue.name}'
                )
                added += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'No venue images found for court: {court.name} ({court.venue.name})'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted!\n'
                f'Court images added: {added}\n'
                f'Courts skipped (already have images): {skipped}\n'
                f'Total court images: {CourtImage.objects.count()}'
            )
        )
