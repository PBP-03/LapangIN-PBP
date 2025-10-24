from django.core.management.base import BaseCommand
from app.venues.models import Venue


class Command(BaseCommand):
    help = 'Update number_of_courts for all venues based on actual court count'

    def handle(self, *args, **options):
        venues = Venue.objects.all()
        updated_count = 0
        
        for venue in venues:
            actual_count = venue.courts.count()
            if venue.number_of_courts != actual_count:
                old_count = venue.number_of_courts
                venue.number_of_courts = actual_count
                venue.save(update_fields=['number_of_courts'])
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated venue "{venue.name}": {old_count} -> {actual_count} courts'
                    )
                )
        
        if updated_count == 0:
            self.stdout.write(self.style.SUCCESS('All venues already have correct court counts!'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} venue(s)'
                )
            )
