from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

# User Model with Role-based Access
class User(AbstractUser):
    USER_ROLES = [
        ('user', 'User/Penyewa'),
        ('mitra', 'Mitra/Pemilik Lapangan'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Fix the reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='backend_user_set',
        related_query_name='backend_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='backend_user_set',
        related_query_name='backend_user',
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

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
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    
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
    category = models.ForeignKey(SportsCategory, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mitra'})
    address = models.TextField()
    location_url = models.URLField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Operational details
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
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
        return f"{self.name} - {self.category}"
    
    @property
    def is_verified(self):
        return self.verification_status == 'approved'

# Venue Images Model
class VenueImage(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='venue_images/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.venue.name} - Image"

# Facility Model
class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='facility_icons/', blank=True, null=True)
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

# Court Model (Individual courts within a venue)
class Court(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='courts')
    name = models.CharField(max_length=100)  # e.g., "Court 1", "Court A"
    is_active = models.BooleanField(default=True)
    maintenance_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.venue.name} - {self.name}"
    
    class Meta:
        unique_together = ('venue', 'name')

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
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='verified_payments')
    notes = models.TextField(blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment for {self.booking}"

# Review Model
class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.booking.court.venue.name} - {self.rating} stars"

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


# Mitra model for admin approval workflow
class Mitra(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    id = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    tanggal_daftar = models.DateTimeField(auto_now_add=True)
    deskripsi = models.TextField(blank=True, null=True)
    gambar = models.ImageField(upload_to='mitra_gambar/', blank=True, null=True)
    alasan_penolakan = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nama} <{self.email}> ({self.status})"
