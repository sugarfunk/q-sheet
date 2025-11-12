"""
Data models and database helpers
Simple functions to interact with the database
"""
from datetime import datetime, date, timedelta
from database import db_transaction


# ==================== LOCATIONS ====================

def get_all_locations(active_only=True):
    """Get all locations, optionally filtered by active status"""
    with db_transaction() as conn:
        query = 'SELECT * FROM locations'
        if active_only:
            query += ' WHERE active = 1'
        query += ' ORDER BY name'
        return conn.execute(query).fetchall()


def get_location(location_id):
    """Get a single location by ID"""
    with db_transaction() as conn:
        return conn.execute(
            'SELECT * FROM locations WHERE id = ?',
            (location_id,)
        ).fetchone()


def create_location(name, address, region='Cherokee', latitude=None, longitude=None):
    """Create a new location"""
    with db_transaction() as conn:
        cursor = conn.execute(
            '''INSERT INTO locations (name, address, region, latitude, longitude)
               VALUES (?, ?, ?, ?, ?)''',
            (name, address, region, latitude, longitude)
        )
        return cursor.lastrowid


def update_location(location_id, **kwargs):
    """Update a location with provided fields"""
    allowed_fields = ['name', 'address', 'region', 'latitude', 'longitude', 'active']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return False

    set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
    values = list(updates.values()) + [location_id]

    with db_transaction() as conn:
        conn.execute(
            f'UPDATE locations SET {set_clause} WHERE id = ?',
            values
        )
        return True


def delete_location(location_id):
    """Delete a location (will cascade to workouts and signups)"""
    with db_transaction() as conn:
        conn.execute('DELETE FROM locations WHERE id = ?', (location_id,))


# ==================== WORKOUTS ====================

def get_workouts_by_location(location_id, active_only=True):
    """Get all workouts for a location"""
    with db_transaction() as conn:
        query = '''SELECT w.*, l.name as location_name
                   FROM workouts w
                   JOIN locations l ON w.location_id = l.id
                   WHERE w.location_id = ?'''
        if active_only:
            query += ' AND w.active = 1'
        query += ' ORDER BY w.day_of_week, w.time'
        return conn.execute(query, (location_id,)).fetchall()


def get_all_workouts(active_only=True):
    """Get all workouts with location info"""
    with db_transaction() as conn:
        query = '''SELECT w.*, l.name as location_name, l.address
                   FROM workouts w
                   JOIN locations l ON w.location_id = l.id'''
        if active_only:
            query += ' WHERE w.active = 1 AND l.active = 1'
        query += ' ORDER BY l.name, w.day_of_week, w.time'
        return conn.execute(query).fetchall()


def get_workout(workout_id):
    """Get a single workout by ID"""
    with db_transaction() as conn:
        return conn.execute(
            '''SELECT w.*, l.name as location_name, l.address
               FROM workouts w
               JOIN locations l ON w.location_id = l.id
               WHERE w.id = ?''',
            (workout_id,)
        ).fetchone()


def create_workout(location_id, day_of_week, time, workout_type='Boot Camp'):
    """Create a new workout schedule"""
    with db_transaction() as conn:
        cursor = conn.execute(
            '''INSERT INTO workouts (location_id, day_of_week, time, workout_type)
               VALUES (?, ?, ?, ?)''',
            (location_id, day_of_week, time, workout_type)
        )
        return cursor.lastrowid


def update_workout(workout_id, **kwargs):
    """Update a workout with provided fields"""
    allowed_fields = ['location_id', 'day_of_week', 'time', 'workout_type', 'active']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return False

    set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
    values = list(updates.values()) + [workout_id]

    with db_transaction() as conn:
        conn.execute(
            f'UPDATE workouts SET {set_clause} WHERE id = ?',
            values
        )
        return True


def delete_workout(workout_id):
    """Delete a workout (will cascade to signups)"""
    with db_transaction() as conn:
        conn.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))


# ==================== Q SIGNUPS ====================

def get_signups_for_date_range(start_date, end_date):
    """Get all Q signups within a date range with workout and location info"""
    with db_transaction() as conn:
        return conn.execute(
            '''SELECT s.*, w.day_of_week, w.time, w.workout_type,
                      l.name as location_name, l.address
               FROM q_signups s
               JOIN workouts w ON s.workout_id = w.id
               JOIN locations l ON w.location_id = l.id
               WHERE s.date >= ? AND s.date <= ?
               ORDER BY s.date, w.time''',
            (start_date, end_date)
        ).fetchall()


def get_signup_for_workout_date(workout_id, workout_date):
    """Get signup for a specific workout on a specific date"""
    with db_transaction() as conn:
        return conn.execute(
            '''SELECT s.*, w.day_of_week, w.time, w.workout_type,
                      l.name as location_name
               FROM q_signups s
               JOIN workouts w ON s.workout_id = w.id
               JOIN locations l ON w.location_id = l.id
               WHERE s.workout_id = ? AND s.date = ?''',
            (workout_id, workout_date)
        ).fetchone()


def create_signup(workout_id, workout_date, q_name, q_email=None, notes=None):
    """Create a new Q signup"""
    with db_transaction() as conn:
        cursor = conn.execute(
            '''INSERT INTO q_signups (workout_id, date, q_name, q_email, notes)
               VALUES (?, ?, ?, ?, ?)''',
            (workout_id, workout_date, q_name, q_email, notes)
        )
        return cursor.lastrowid


def update_signup(signup_id, **kwargs):
    """Update a signup with provided fields"""
    allowed_fields = ['q_name', 'q_email', 'notes', 'reminded']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not updates:
        return False

    set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
    values = list(updates.values()) + [signup_id]

    with db_transaction() as conn:
        conn.execute(
            f'UPDATE q_signups SET {set_clause} WHERE id = ?',
            values
        )
        return True


def delete_signup(signup_id):
    """Delete a Q signup"""
    with db_transaction() as conn:
        conn.execute('DELETE FROM q_signups WHERE id = ?', (signup_id,))


def get_empty_slots(start_date, end_date):
    """Get all workout slots without Q signups in date range"""
    with db_transaction() as conn:
        # This is a bit complex - we need to generate all possible workout dates
        # and then left join with signups to find empties
        return conn.execute(
            '''SELECT w.id as workout_id, w.day_of_week, w.time, w.workout_type,
                      l.id as location_id, l.name as location_name, l.address
               FROM workouts w
               JOIN locations l ON w.location_id = l.id
               WHERE w.active = 1 AND l.active = 1
               ORDER BY w.day_of_week, w.time''',
        ).fetchall()


# ==================== STATISTICS ====================

def get_coverage_stats(start_date, end_date):
    """Get coverage statistics for a date range"""
    # Generate all workout instances in the date range
    workouts = get_all_workouts(active_only=True)
    signups = get_signups_for_date_range(start_date, end_date)

    # Create a set of (workout_id, date) tuples that have signups
    covered = {(s['workout_id'], s['date']) for s in signups}

    # Count total slots and covered slots
    total_slots = 0
    current = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    while current <= end:
        day_of_week = current.weekday()
        # Convert Python weekday (Mon=0) to our format (Sun=0)
        db_day = (day_of_week + 1) % 7

        for workout in workouts:
            if workout['day_of_week'] == db_day:
                total_slots += 1

        current += timedelta(days=1)

    covered_slots = len(covered)

    return {
        'total_slots': total_slots,
        'covered_slots': covered_slots,
        'empty_slots': total_slots - covered_slots,
        'coverage_percent': (covered_slots / total_slots * 100) if total_slots > 0 else 0
    }


# ==================== UTILITY FUNCTIONS ====================

def get_day_name(day_of_week):
    """Convert day_of_week integer to name"""
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return days[day_of_week]


def get_day_abbr(day_of_week):
    """Convert day_of_week integer to abbreviation"""
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    return days[day_of_week]
