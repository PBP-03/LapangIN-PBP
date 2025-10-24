from django.db import models
from django.core.validators import MinValueValidator
from app.users.models import User
from app.courts.models import Court, CourtSession
import uuid

# Booking Model
class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'user'})
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    session = models.ForeignKey(CourtSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0.5)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status fields
    booking_status = models.CharField(max_length=10, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='unpaid')
    
    # Additional info
    notes = models.TextField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.court.venue.name} ({self.booking_date})"
    
    class Meta:
        unique_together = ('court', 'booking_date', 'start_time')

# Payment Model
class Payment(models.Model):
    PAYMENT_METHOD = [
        ('bank_transfer', 'Bank Transfer'),
        ('e_wallet', 'E-Wallet'),
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_proof = models.URLField(max_length=500, blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='verified_payments')
    notes = models.TextField(blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment for {self.booking}"

