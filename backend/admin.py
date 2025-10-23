from django.contrib import admin
from .models import (
    User, SportsCategory, Venue, VenueImage, Facility, VenueFacility,
    Court, CourtSession, CourtImage, OperationalHour, Booking, Payment, Review, ActivityLog, Pendapatan
)

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'created_at')
    list_filter = ('role', 'is_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(SportsCategory)
class SportsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'verification_status', 'created_at')
    list_filter = ('verification_status',)
    search_fields = ('name', 'address', 'owner__username')


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'category', 'price_per_hour', 'is_active')
    list_filter = ('is_active', 'venue', 'category')
    search_fields = ('name', 'venue__name')


@admin.register(CourtSession)
class CourtSessionAdmin(admin.ModelAdmin):
    list_display = ('court', 'session_name', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active', 'court')
    search_fields = ('session_name', 'court__name')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'court', 'booking_date', 'start_time', 'booking_status', 'payment_status', 'created_at')
    list_filter = ('booking_status', 'payment_status', 'booking_date')
    search_fields = ('user__username', 'court__venue__name')


@admin.register(Pendapatan)
class PendapatanAdmin(admin.ModelAdmin):
    list_display = ('mitra', 'booking', 'amount', 'commission_amount', 'net_amount', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'mitra')
    search_fields = ('mitra__username', 'booking__court__venue__name')
    readonly_fields = ('commission_amount', 'net_amount')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'paid_at')
    list_filter = ('payment_method',)
    search_fields = ('booking__user__username', 'transaction_id')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'description', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('user__username', 'description')


# Register other models
admin.site.register(VenueImage)
admin.site.register(CourtImage)
admin.site.register(Facility)
admin.site.register(VenueFacility)
admin.site.register(OperationalHour)
admin.site.register(Review)
