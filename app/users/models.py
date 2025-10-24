from django.db import models
from django.contrib.auth.models import AbstractUser
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
    profile_picture = models.URLField(max_length=500, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Fix the reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='users_user_set',
        related_query_name='users_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='users_user_set',
        related_query_name='users_user',
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
