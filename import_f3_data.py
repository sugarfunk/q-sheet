"""
Import F3 location and workout data
This script helps import workout locations and schedules from various sources
"""
import sqlite3
import re
from datetime import datetime
from database import init_db, db_transaction
import models


# Sample data structure based on f3cherokee.com/locations
# In production, you could scrape this or provide a CSV upload interface
SAMPLE_F3_DATA = [
    {
        'name': 'Apex',
        'address': '6565 Putnam Ford Dr, Woodstock, GA',
        'days': ['Monday', 'Thursday'],
        'time': '05:30',
        'workout_type': 'Boot Camp'
    },
    {
        'name': 'Arena',
        'address': '6688 Bells Ferry Rd, Woodstock, GA',
        'days': ['Thursday'],
        'time': '05:30',
        'workout_type': 'Boot Camp'
    },
    {
        'name': 'Armory',
        'address': '930 Marietta HWY, Canton, GA',
        'days': ['Friday'],
        'time': '05:30',
        'workout_type': 'Boot Camp'
    },
    {
        'name': 'Blacktop',
        'address': '150 Ridgewalk Pkwy, Woodstock, GA',
        'days': ['Friday'],
        'time': '05:00',
        'workout_type': 'Boot Camp'
    },
    {
        'name': 'Brickyard',
        'address': '130 E Main St, Canton, GA',
        'days': ['Tuesday'],
        'time': '05:00',
        'workout_type': 'Run'
    },
    {
        'name': 'Camelot',
        'address': '1100 Towne Lake Pkwy, Woodstock, GA',
        'days': ['Monday', 'Wednesday', 'Friday'],
        'time': '05:30',
        'workout_type': 'Boot Camp'
    },
    {
        'name': 'The Clinic',
        'address': '1776 Heritage Walk, Woodstock, GA',
        'days': ['Tuesday', 'Thursday', 'Saturday'],
        'time': '05:30',
        'workout_type': 'Boot Camp'
    },
    {
        'name': 'Shamrock',
        'address': '5865 Bells Ferry Rd, Acworth, GA',
        'days': ['Wednesday', 'Saturday'],
        'time': '05:30',
        'workout_type': 'Boot Camp'
    },
]


def day_name_to_number(day_name):
    """Convert day name to database format (0=Sunday, 1=Monday, etc.)"""
    days = {
        'Sunday': 0,
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6
    }
    return days.get(day_name, -1)


def parse_time(time_str):
    """Parse time string to HH:MM format"""
    # Handle formats like "05:30", "5:30 AM", "05:30-06:15 AM"
    time_str = time_str.strip()

    # Extract just the start time
    if '-' in time_str:
        time_str = time_str.split('-')[0].strip()

    # Remove AM/PM if present
    time_str = re.sub(r'\s*(AM|PM|am|pm)', '', time_str)

    # Parse and format
    try:
        # Try parsing as HH:MM
        time_obj = datetime.strptime(time_str, '%H:%M')
        return time_obj.strftime('%H:%M')
    except ValueError:
        try:
            # Try parsing as H:MM
            time_obj = datetime.strptime(time_str, '%I:%M')
            return time_obj.strftime('%H:%M')
        except ValueError:
            # Default to 05:30
            return '05:30'


def import_sample_data():
    """Import sample F3 Cherokee data"""
    print("Importing F3 Cherokee sample data...")

    imported_locations = 0
    imported_workouts = 0

    for location_data in SAMPLE_F3_DATA:
        try:
            # Check if location already exists
            existing_loc = None
            with db_transaction() as conn:
                result = conn.execute(
                    'SELECT id FROM locations WHERE name = ?',
                    (location_data['name'],)
                ).fetchone()
                if result:
                    existing_loc = result['id']

            # Create or get location
            if existing_loc:
                location_id = existing_loc
                print(f"  Location already exists: {location_data['name']}")
            else:
                location_id = models.create_location(
                    name=location_data['name'],
                    address=location_data['address'],
                    region='Cherokee'
                )
                imported_locations += 1
                print(f"  ✓ Created location: {location_data['name']}")

            # Create workouts for each day
            time = parse_time(location_data['time'])
            for day_name in location_data['days']:
                day_num = day_name_to_number(day_name)
                if day_num == -1:
                    continue

                # Check if workout already exists
                with db_transaction() as conn:
                    existing = conn.execute(
                        '''SELECT id FROM workouts
                           WHERE location_id = ? AND day_of_week = ? AND time = ?''',
                        (location_id, day_num, time)
                    ).fetchone()

                if not existing:
                    models.create_workout(
                        location_id=location_id,
                        day_of_week=day_num,
                        time=time,
                        workout_type=location_data.get('workout_type', 'Boot Camp')
                    )
                    imported_workouts += 1
                    print(f"    ✓ Created workout: {day_name} at {time}")

        except Exception as e:
            print(f"  ✗ Error importing {location_data['name']}: {e}")

    print(f"\nImport complete!")
    print(f"  Locations: {imported_locations} created")
    print(f"  Workouts: {imported_workouts} created")


def import_from_csv(csv_file):
    """
    Import from CSV file
    Expected format: Location,Address,Day,Time,Type
    Example: Apex,6565 Putnam Ford Dr,Monday,05:30,Boot Camp
    """
    import csv

    print(f"Importing from CSV: {csv_file}")

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Implementation similar to import_sample_data
            pass


if __name__ == '__main__':
    import sys

    # Initialize database first
    print("Initializing database...")
    init_db()

    # Import sample data
    if len(sys.argv) > 1 and sys.argv[1] == '--csv':
        import_from_csv(sys.argv[2])
    else:
        import_sample_data()

    print("\nDone! You can now run the application with: python app.py")
