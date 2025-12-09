from app.venues.models import Venue, SportsCategory, Facility
from app.courts.models import Court
from django.db.models import Count

print("=" * 60)
print("DATABASE SEEDING VERIFICATION")
print("=" * 60)

print(f"\nTotal Venues: {Venue.objects.count()}")
print(f"Total Courts: {Court.objects.count()}")
print(f"Total Facilities: {Facility.objects.count()}")
print(f"Total Sports Categories: {SportsCategory.objects.count()}")

print("\n" + "-" * 60)
print("VENUES BY CATEGORY:")
print("-" * 60)
venues_by_cat = Court.objects.values('category__name').annotate(count=Count('id')).order_by('-count')
for v in venues_by_cat:
    print(f"  {v['category__name']}: {v['count']} courts")

print("\n" + "-" * 60)
print("FIRST 10 VENUES:")
print("-" * 60)
for venue in Venue.objects.all()[:10]:
    print(f"  - {venue.name}")
    print(f"    Courts: {venue.number_of_courts} | Status: {venue.verification_status}")
    print(f"    Address: {venue.address[:50]}...")
    print()

print("\n" + "-" * 60)
print("AVAILABLE FACILITIES:")
print("-" * 60)
for facility in Facility.objects.all()[:15]:
    print(f"  - {facility.name}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE!")
print("=" * 60)
