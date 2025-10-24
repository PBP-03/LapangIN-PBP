from django.db import models
from django.core.validators import MinValueValidator
from app.venues.models import Venue, SportsCategory

# Court Model (Individual courts within a venue)
class Court(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='courts')
    name = models.CharField(max_length=100)  # e.g., "Court 1", "Court A"
    category = models.ForeignKey(SportsCategory, on_delete=models.CASCADE, null=True, blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    is_active = models.BooleanField(default=True)
    maintenance_notes = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # Additional court description
    
    def __str__(self):
        return f"{self.venue.name} - {self.name} ({self.category.get_name_display() if self.category else 'No Category'})"
    
    class Meta:
        unique_together = ('venue', 'name')

# Court Time Slots / Sessions Model
class CourtSession(models.Model):
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='sessions')
    session_name = models.CharField(max_length=100)  # e.g., "Morning Session", "Session 1"
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.court.name} - {self.session_name} ({self.start_time}-{self.end_time})"
    
    class Meta:
        unique_together = ('court', 'start_time')
        ordering = ['start_time']

# Court Images Model
class CourtImage(models.Model):
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500)
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.court.venue.name} - {self.court.name} - Image"

