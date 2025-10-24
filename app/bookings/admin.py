from django.contrib import admin
from .models import Booking, Payment

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'court', 'booking_date', 'start_time', 'booking_status', 'payment_status', 'created_at')
    list_filter = ('booking_status', 'payment_status', 'booking_date')
    search_fields = ('user__username', 'court__venue__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'paid_at')
    list_filter = ('payment_method',)
    search_fields = ('booking__user__username', 'transaction_id')

