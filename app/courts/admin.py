from django.contrib import admin
from .models import Court, CourtSession, CourtImage

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


# Register other models
admin.site.register(CourtImage)

