from django.core.management.base import BaseCommand
from django.utils import timezone
from app.bookings.models import Booking
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Mark paid bookings as completed if their booking date/time has passed'

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()
        
        # Find bookings that should be completed:
        # - booking_status is 'confirmed' or 'pending'
        # - payment_status is 'paid'
        # - booking_date is today or in the past
        # - end_time has passed (if booking_date is today)
        
        bookings_to_complete = Booking.objects.filter(
            booking_status__in=['confirmed', 'pending'],
            payment_status='paid'
        )
        
        completed_count = 0
        for booking in bookings_to_complete:
            # Check if the booking time has passed
            booking_datetime = datetime.combine(booking.booking_date, booking.end_time)
            booking_datetime = timezone.make_aware(booking_datetime)
            
            if booking_datetime < now:
                booking.booking_status = 'completed'
                booking.save()
                completed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Completed booking {booking.id} for {booking.user.username} '
                        f'at {booking.court.venue.name} on {booking.booking_date}'
                    )
                )
        
        if completed_count == 0:
            self.stdout.write(self.style.WARNING('No bookings to mark as completed'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nTotal bookings marked as completed: {completed_count}')
            )
