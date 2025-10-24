from django.contrib import admin
from .models import SportsCategory, Venue, VenueImage, Facility, VenueFacility, OperationalHour

@admin.register(SportsCategory)
class SportsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'verification_status', 'created_at')
    list_filter = ('verification_status',)
    search_fields = ('name', 'address', 'owner__username')


# Register other models
admin.site.register(VenueImage)
admin.site.register(Facility)
admin.site.register(VenueFacility)
admin.site.register(OperationalHour)

