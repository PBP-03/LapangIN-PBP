# LapangIN Seed Command Documentation

## Overview
I've created a new Django management command `seed_from_json` that populates your database with realistic data based on your existing `data.json` file. This command reads the venue data from your JSON file and generates comprehensive seed data for your entire application.

## Command Location
```
app/users/management/commands/seed_from_json.py
```

## Features

### What the command creates:
1. **Venues from JSON**: All venues from your `data.json` file with proper categorization
2. **Users**: Admin, mitra (venue owners), and regular users 
3. **Sports Categories**: FUTSAL, BADMINTON, BASKET, TENNIS, PADEL, VOLI
4. **Facilities**: All facilities mentioned in your JSON data plus additional common ones
5. **Courts**: Individual courts for each venue based on `jumlahLapangan`
6. **Operational Hours**: Based on the `OperationalHours` from JSON data
7. **Images**: Uses the image files you already have in `static/img/dataset-photos/`
8. **Bookings**: Realistic booking data for the past month and next 2 weeks
9. **Payments**: Payment records for confirmed bookings
10. **Reviews**: User reviews for completed bookings
11. **Revenue (Pendapatan)**: Commission and payment tracking for mitras
12. **Activity Logs**: User activity tracking

### Data Mapping from JSON:
- `name` → Venue name
- `Category` → Sports category (FUTSAL, BADMINTON, etc.)
- `address` → Venue address
- `location` → Google Maps URL
- `Contact` → Phone number (automatically formats Indonesian numbers)
- `jumlahLapangan` → Number of courts
- `OperationalHours` → Daily operating hours (7 days array)
- `Facilities` → Available facilities
- `Price` → Price per hour for courts
- `Image` → Uses your existing photos in dataset-photos folder

## Usage

### Prerequisites
Make sure you have Django installed and your virtual environment activated:

```bash
# Activate your virtual environment (if you have one)
source venv/bin/activate  # or your specific activation command

# Install requirements if not already done
pip install -r requirements.txt
```

### Running the Command

#### Basic usage (keeps existing data):
```bash
python manage.py seed_from_json
```

#### Clear existing data and reseed:
```bash
python manage.py seed_from_json --clear
```

**⚠️ Warning**: The `--clear` option will delete ALL existing data in your database!

### Command Output
The command provides detailed feedback about what it's creating:
```
Starting data seeding from JSON...
Loaded 89 venues from JSON file
Creating users...
Created 18 users
Creating sports categories...
Created 6 sports categories
Creating facilities...
Created 45 facilities
Creating venues from JSON data...
Created 89 venues from JSON data
... (and so on)
```

## Generated Data Details

### Users Created:
- **1 Admin**: `admin` / `admin123`
- **10 Mitras**: Various venue owners with credentials `mitra123`
- **8 Regular Users**: For testing bookings with credentials `user123`

### Venues:
- All 89+ venues from your JSON file
- Properly categorized by sport type
- Realistic descriptions generated
- Contact information formatted
- Verification status set to "approved"

### Bookings:
- 150+ realistic bookings
- Mix of past (completed/cancelled) and future (confirmed/pending)
- Realistic time slots and durations
- Proper payment status correlation

### Images:
- Uses your existing photos from `static/img/dataset-photos/`
- Matches image filenames from JSON data
- Automatic fallback for missing images

## Data Structure

The command follows your Django model relationships:
```
User → owns → Venue → contains → Court → has → Booking → generates → Revenue
            ↓         ↓           ↓
         Facilities  Images   Court Sessions
```

## Troubleshooting

### Common Issues:

1. **Django not found**: Make sure your virtual environment is activated
2. **Permission errors**: Ensure you have write access to the database
3. **Missing images**: The command handles missing images gracefully with fallbacks
4. **Large dataset**: The command may take a few minutes for all the data generation

### Database Reset:
If you need to completely start over:
```bash
# For SQLite (if using)
rm db.sqlite3
python manage.py migrate
python manage.py seed_from_json
```

## Customization

You can modify the command to:
- Change the number of bookings generated
- Adjust user profiles
- Modify facility mappings
- Change operational hour patterns
- Customize review comments

## File Dependencies
- `static/dataset/data.json` - Your venue data source
- `static/img/dataset-photos/` - Image files referenced in JSON
- All Django models in your app

## Notes
- The command is idempotent (safe to run multiple times without `--clear`)
- Images are referenced by URL path, not uploaded files
- All dates and times are relative to the current date
- Commission rates and other business logic can be customized in the code

This command gives you a fully populated database with realistic data that represents your actual venue portfolio, making it perfect for development and testing!