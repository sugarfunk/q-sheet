"""
F3 Q-Sheet - Fast, Simple Workout Sign-Up Application
Main Flask application with routes
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime, date, timedelta
from functools import wraps
import os

from config import get_config
from database import init_db, get_setting, set_setting
import models

# Initialize Flask app
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Initialize database on first run
if not os.path.exists(config.DATABASE_PATH):
    init_db()


# ==================== AUTHENTICATION ====================

def check_signup_password(password):
    """Check if signup password is correct"""
    stored = get_setting('signup_password', config.SIGNUP_PASSWORD)
    return password == stored


def check_admin_password(password):
    """Check if admin password is correct"""
    stored = get_setting('admin_password', config.ADMIN_PASSWORD)
    return password == stored


def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Homepage with weekly schedule view"""
    # Get current week (Monday to Sunday)
    today = date.today()
    # Find Monday of current week
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    sunday = monday + timedelta(days=6)

    # Get all workouts and signups for the week
    workouts = models.get_all_workouts(active_only=True)
    signups = models.get_signups_for_date_range(
        monday.strftime('%Y-%m-%d'),
        sunday.strftime('%Y-%m-%d')
    )

    # Create a lookup for signups by (workout_id, date)
    signup_lookup = {
        (s['workout_id'], s['date']): s for s in signups
    }

    # Organize workouts by day and time
    schedule = {}
    for i in range(7):
        day = monday + timedelta(days=i)
        db_day = (day.weekday() + 1) % 7  # Convert to our format (Sun=0)
        schedule[day.strftime('%Y-%m-%d')] = {
            'date': day,
            'day_name': models.get_day_name(db_day),
            'workouts': []
        }

    # Add workouts to schedule
    for workout in workouts:
        for day_str in schedule:
            day = schedule[day_str]['date']
            db_day = (day.weekday() + 1) % 7
            if workout['day_of_week'] == db_day:
                signup = signup_lookup.get((workout['id'], day_str))
                schedule[day_str]['workouts'].append({
                    'workout': workout,
                    'signup': signup,
                    'date': day_str
                })

    # Sort workouts by time within each day
    for day_str in schedule:
        schedule[day_str]['workouts'].sort(key=lambda x: x['workout']['time'])

    return render_template('index.html',
                         schedule=schedule,
                         monday=monday,
                         sunday=sunday,
                         today=today)


@app.route('/schedule/week/<int:offset>')
def week_schedule(offset):
    """View schedule for a specific week offset from current week"""
    today = date.today()
    days_since_monday = today.weekday()
    base_monday = today - timedelta(days=days_since_monday)
    monday = base_monday + timedelta(weeks=offset)
    sunday = monday + timedelta(days=6)

    workouts = models.get_all_workouts(active_only=True)
    signups = models.get_signups_for_date_range(
        monday.strftime('%Y-%m-%d'),
        sunday.strftime('%Y-%m-%d')
    )

    signup_lookup = {
        (s['workout_id'], s['date']): s for s in signups
    }

    schedule = {}
    for i in range(7):
        day = monday + timedelta(days=i)
        db_day = (day.weekday() + 1) % 7
        schedule[day.strftime('%Y-%m-%d')] = {
            'date': day,
            'day_name': models.get_day_name(db_day),
            'workouts': []
        }

    for workout in workouts:
        for day_str in schedule:
            day = schedule[day_str]['date']
            db_day = (day.weekday() + 1) % 7
            if workout['day_of_week'] == db_day:
                signup = signup_lookup.get((workout['id'], day_str))
                schedule[day_str]['workouts'].append({
                    'workout': workout,
                    'signup': signup,
                    'date': day_str
                })

    for day_str in schedule:
        schedule[day_str]['workouts'].sort(key=lambda x: x['workout']['time'])

    return render_template('week_schedule.html',
                         schedule=schedule,
                         monday=monday,
                         sunday=sunday,
                         today=today,
                         offset=offset)


@app.route('/signup/<int:workout_id>/<date_str>', methods=['GET', 'POST'])
def signup(workout_id, date_str):
    """Sign up to Q a workout"""
    workout = models.get_workout(workout_id)
    if not workout:
        return "Workout not found", 404

    existing = models.get_signup_for_workout_date(workout_id, date_str)

    if request.method == 'POST':
        password = request.form.get('password', '')
        q_name = request.form.get('q_name', '').strip()
        q_email = request.form.get('q_email', '').strip() or None
        notes = request.form.get('notes', '').strip() or None

        # Validate password
        if not check_signup_password(password):
            return render_template('signup.html',
                                 workout=workout,
                                 date_str=date_str,
                                 existing=existing,
                                 error="Invalid password")

        # Validate Q name
        if not q_name:
            return render_template('signup.html',
                                 workout=workout,
                                 date_str=date_str,
                                 existing=existing,
                                 error="Please enter your name")

        # Check if slot is already taken
        if existing:
            return render_template('signup.html',
                                 workout=workout,
                                 date_str=date_str,
                                 existing=existing,
                                 error="This slot is already taken")

        # Create signup
        models.create_signup(workout_id, date_str, q_name, q_email, notes)

        return render_template('signup_success.html',
                             workout=workout,
                             date_str=date_str,
                             q_name=q_name)

    return render_template('signup.html',
                         workout=workout,
                         date_str=date_str,
                         existing=existing)


@app.route('/locations')
def locations():
    """List all locations"""
    all_locations = models.get_all_locations(active_only=True)
    return render_template('locations.html', locations=all_locations)


@app.route('/location/<int:location_id>')
def location_detail(location_id):
    """View a specific location's schedule"""
    location = models.get_location(location_id)
    if not location:
        return "Location not found", 404

    workouts = models.get_workouts_by_location(location_id, active_only=True)

    # Get next 4 weeks of signups
    today = date.today()
    end_date = today + timedelta(days=28)

    signups = models.get_signups_for_date_range(
        today.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

    # Organize by workout
    workout_signups = {}
    for signup in signups:
        if signup['workout_id'] not in workout_signups:
            workout_signups[signup['workout_id']] = []
        workout_signups[signup['workout_id']].append(signup)

    return render_template('location_detail.html',
                         location=location,
                         workouts=workouts,
                         workout_signups=workout_signups)


# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_admin_password(password):
            session['admin_logged_in'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html', error="Invalid password")

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with statistics"""
    # Get stats for next 4 weeks
    today = date.today()
    end_date = today + timedelta(days=28)

    stats = models.get_coverage_stats(
        today.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

    # Get upcoming signups
    recent_signups = models.get_signups_for_date_range(
        today.strftime('%Y-%m-%d'),
        (today + timedelta(days=7)).strftime('%Y-%m-%d')
    )

    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_signups=recent_signups)


@app.route('/admin/locations')
@login_required
def admin_locations():
    """Manage locations"""
    all_locations = models.get_all_locations(active_only=False)
    return render_template('admin/locations.html', locations=all_locations)


@app.route('/admin/workouts')
@login_required
def admin_workouts():
    """Manage workouts"""
    all_workouts = models.get_all_workouts(active_only=False)
    return render_template('admin/workouts.html', workouts=all_workouts)


@app.route('/admin/signups')
@login_required
def admin_signups():
    """Manage signups"""
    today = date.today()
    end_date = today + timedelta(days=28)
    signups = models.get_signups_for_date_range(
        today.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    return render_template('admin/signups.html', signups=signups)


# ==================== API ROUTES ====================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """API endpoint for creating a signup"""
    data = request.get_json()

    workout_id = data.get('workout_id')
    date_str = data.get('date')
    q_name = data.get('q_name', '').strip()
    q_email = data.get('q_email', '').strip() or None
    password = data.get('password', '')
    notes = data.get('notes', '').strip() or None

    # Validate
    if not check_signup_password(password):
        return jsonify({'error': 'Invalid password'}), 401

    if not q_name:
        return jsonify({'error': 'Name is required'}), 400

    # Check if already taken
    existing = models.get_signup_for_workout_date(workout_id, date_str)
    if existing:
        return jsonify({'error': 'Slot already taken'}), 409

    # Create signup
    signup_id = models.create_signup(workout_id, date_str, q_name, q_email, notes)

    return jsonify({
        'success': True,
        'signup_id': signup_id,
        'message': 'Q signup successful!'
    }), 201


@app.route('/api/notifications/recent', methods=['GET'])
def api_notifications_recent():
    """API endpoint for recent signups (for notifications)"""
    hours = request.args.get('hours', 24, type=int)
    cutoff = datetime.now() - timedelta(hours=hours)

    with models.db_transaction() as conn:
        signups = conn.execute(
            '''SELECT s.*, w.day_of_week, w.time, w.workout_type,
                      l.name as location_name
               FROM q_signups s
               JOIN workouts w ON s.workout_id = w.id
               JOIN locations l ON w.location_id = l.id
               WHERE s.created_at >= ?
               ORDER BY s.created_at DESC''',
            (cutoff.strftime('%Y-%m-%d %H:%M:%S'),)
        ).fetchall()

    return jsonify([dict(s) for s in signups])


@app.route('/api/notifications/upcoming', methods=['GET'])
def api_notifications_upcoming():
    """API endpoint for upcoming workouts needing reminders"""
    days = request.args.get('days', 2, type=int)
    reminder_date = (date.today() + timedelta(days=days)).strftime('%Y-%m-%d')

    with models.db_transaction() as conn:
        signups = conn.execute(
            '''SELECT s.*, w.day_of_week, w.time, w.workout_type,
                      l.name as location_name, l.address
               FROM q_signups s
               JOIN workouts w ON s.workout_id = w.id
               JOIN locations l ON w.location_id = l.id
               WHERE s.date = ? AND s.reminded = 0 AND s.q_email IS NOT NULL
               ORDER BY w.time''',
            (reminder_date,)
        ).fetchall()

    return jsonify([dict(s) for s in signups])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=config.DEBUG)
