from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from app.users.models import User
from app.bookings.models import Booking
import uuid

# Pendapatan/Revenue Model (for mitra revenue tracking)
class Pendapatan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mitra = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mitra'}, related_name='pendapatan')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='pendapatan')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, validators=[MinValueValidator(0), MaxValueValidator(100)])  # Platform commission percentage
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])  # Amount after commission
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calculate commission and net amount
        self.commission_amount = (self.amount * self.commission_rate) / 100
        self.net_amount = self.amount - self.commission_amount
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.mitra.username} - {self.booking.court.venue.name} - Rp {self.net_amount}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Pendapatan"

# Activity Log Model (for admin monitoring)
class ActivityLog(models.Model):
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('verification', 'Verification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action_type} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']

