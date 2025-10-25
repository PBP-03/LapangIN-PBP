from django.db import models
from django.core.validators import MinValueValidator
from app.users.models import User
import uuid

# Sports Category Model
class SportsCategory(models.Model):
    CATEGORY_CHOICES = [
        ('FUTSAL', 'Futsal'),
        ('BADMINTON', 'Badminton'),
        ('BASKET', 'Basket'),
        ('TENIS', 'Tenis'),
        ('PADEL', 'Padel'),
        ('VOLI', 'Voli'),
    ]
    
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.URLField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return self.get_name_display()

# Venue/Lapangan Model
class Venue(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mitra'})
    address = models.TextField()
    location_url = models.URLField(max_length=500, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Operational details
    number_of_courts = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Verification
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='verified_venues', limit_choices_to={'role': 'admin'})
    verification_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_verified(self):
        return self.verification_status == 'approved'

# Venue Images Model
class VenueImage(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500)
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.venue.name} - Image"

# Facility Model
class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Facilities"

# Venue Facilities (Many-to-Many relationship)
class VenueFacility(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('venue', 'facility')
    
    def __str__(self):
        return f"{self.venue.name} - {self.facility.name}"

# Operational Hours Model
class OperationalHour(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'), 
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='operational_hours')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.venue.name} - {self.get_day_of_week_display()}: {self.open_time}-{self.close_time}"
    
    class Meta:
        unique_together = ('venue', 'day_of_week')

