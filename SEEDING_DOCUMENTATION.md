# Data Seeding Documentation

## Overview
This document explains the data seeding process for the LapangIN application, which populates the Django database with venue, court, and facility data from the JSON dataset.

## Seeding Summary

### Data Source
- **File**: `static/dataset/data.json`
- **Total Records**: 123 venue entries
- **Categories**: BADMINTON, BASKET, FUTSAL, PADEL, TENNIS

### Seeding Results
✅ **Venues Created**: 99 unique venues
✅ **Venues Updated**: 24 (duplicates consolidated)
✅ **Courts Generated**: 225 courts across all venues
✅ **Facilities Imported**: 29 different facilities
✅ **Sports Categories**: 5 (BADMINTON, BASKET, FUTSAL, TENIS, PADEL)

### Database Statistics
```
Total Venues: 99
Total Courts: 225
Total Facilities: 29
Total Sports Categories: 5

Courts by Category:
  - BADMINTON: 89 courts
  - PADEL: 57 courts
  - FUTSAL: 40 courts
  - BASKET: 20 courts
  - TENIS: 19 courts
```

## Seeding Command

### How to Run
```bash
cd "c:\Users\Rayyan\Downloads\Pemrograman Berbasis Platform\TK Flutter Test\LapangIN-PBP"
python manage.py seed_venues
```

### What It Does
1. **Creates Default Users**:
   - `mitra_admin` (role: mitra) - Default venue owner
   - `admin` (role: admin) - Default admin for verification

2. **Imports Venues**:
   - Name, address, location URL, contact
   - Number of courts
   - Verification status (auto-approved)

3. **Generates Courts**:
   - Creates individual courts based on `jumlahLapangan`
   - Assigns sports category
   - Sets price per hour

4. **Adds Facilities**:
   - Creates facility records
   - Links facilities to venues (many-to-many)

5. **Sets Operational Hours**:
   - Parses time strings (e.g., "08.00 - 23.00")
   - Creates records for each day of the week

6. **Imports Images**:
   - Links image URLs to venues
   - Sets first image as primary

## Data Mapping

### JSON to Django Model

| JSON Field | Django Model | Field |
|------------|-------------|-------|
| name | Venue | name |
| address | Venue | address |
| location | Venue | location_url |
| Contact | Venue | contact |
| jumlahLapangan | Venue | number_of_courts |
| Category | Court | category (via SportsCategory) |
| Price | Court | price_per_hour |
| Facilities | VenueFacility | facility (many-to-many) |
| OperationalHours | OperationalHour | open_time, close_time |
| Image | VenueImage | image_url |

### Category Mapping
```python
'BADMINTON' → 'BADMINTON'
'BASKET' → 'BASKET'
'FUTSAL' → 'FUTSAL'
'TENNIS' → 'TENIS'
'PADEL' → 'PADEL'
```

## Verification

### Check Seeded Data
```bash
# Run verification script
Get-Content verify_seeding.py | python manage.py shell
```

### Sample Venues
1. **JiFi Badminton** - 3 courts, Jakarta Selatan
2. **Katamaran Indah Function Hall** - 2 courts, Jakarta Utara
3. **VIE Arena, Badminton Hall** - 6 courts, Tangerang
4. **Sky Badminton Sport** - 8 courts, Tangerang
5. **Namapa Arena** - 2 courts, Tangerang Selatan

### Available Facilities
- Jual Minuman
- Jual Makanan Ringan
- Parkir / Parkir Mobil / Parkir Motor
- Toilet
- Wi-Fi
- Cafe & Resto
- Shower / Hot Shower
- Ruang Ganti
- Musholla
- Tribun Penonton
- And more...

## API Endpoints

### Fetch All Venues
```
GET http://127.0.0.1:8000/api/venues/
```

### Fetch Venue by ID
```
GET http://127.0.0.1:8000/api/venues/{uuid}/
```

### Fetch Courts by Venue
```
GET http://127.0.0.1:8000/api/venues/{uuid}/courts/
```

## Flutter Integration

### Testing from Flutter App
1. Ensure Django server is running: `python manage.py runserver`
2. Open Flutter app
3. Navigate to home page - venues should load automatically
4. Click on any venue to see details

### Expected Behavior
- **Home Page**: Displays list of 99 venues with names and images
- **Venue Detail**: Shows full venue information, courts, facilities
- **Booking**: Courts are available for booking with correct prices
- **Search/Filter**: Can filter by sport category

## Troubleshooting

### Re-run Seeding
If you need to re-seed (e.g., after database reset):
```bash
python manage.py seed_venues
```
The command is idempotent - it will create new venues or update existing ones.

### Clear All Data
```bash
# Delete all venues (cascades to courts, images, etc.)
python manage.py shell -c "from app.venues.models import Venue; Venue.objects.all().delete()"

# Then re-seed
python manage.py seed_venues
```

### Check Django Admin
1. Go to http://127.0.0.1:8000/admin/
2. Login with: `admin` / `admin123`
3. Navigate to Venues, Courts, Facilities to view data

## Default Credentials

### Admin User
- **Username**: admin
- **Password**: admin123
- **Role**: admin

### Mitra User
- **Username**: mitra_admin
- **Password**: mitra123
- **Role**: mitra

## Notes

### Image Handling
- Images are referenced as: `/static/dataset/images/{filename}`
- Original images from JSON are preserved in filenames
- Flutter app uses `cached_network_image` to load images
- Full URL: `http://127.0.0.1:8000/static/dataset/images/{filename}`

### Data Quality
- **Contact numbers**: Some venues have null contact info
- **Duplicates**: 24 duplicate venue names were consolidated
- **Operational hours**: All venues have 7-day schedules
- **Verification**: All seeded venues are auto-approved for testing

### Performance
- **Seeding time**: ~10-15 seconds for 123 records
- **Database size**: Minimal (SQLite3 ~5MB)
- **API response**: Fast (<100ms for venue list)

## Next Steps

### For Development
1. ✅ Data seeded successfully
2. ✅ Django API endpoints working
3. 🔄 Test Flutter app with real data
4. 🔄 Verify images display correctly
5. 🔄 Test booking flow with seeded courts

### For Production
1. Switch to PostgreSQL
2. Add more real venue images
3. Create more diverse test data
4. Add reviews and bookings seed data
5. Configure media file handling

---

**Last Updated**: December 4, 2025
**Seeding Command**: `python manage.py seed_venues`
**Status**: ✅ Completed Successfully
