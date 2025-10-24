from django.contrib import admin
from .models import Pendapatan, ActivityLog

@admin.register(Pendapatan)
class PendapatanAdmin(admin.ModelAdmin):
    list_display = ('mitra', 'booking', 'amount', 'commission_amount', 'net_amount', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'mitra')
    search_fields = ('mitra__username', 'booking__court__venue__name')
    readonly_fields = ('commission_amount', 'net_amount')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'description', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('user__username', 'description')

