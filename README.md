# F3 Q-Sheet - Fast Workout Sign-Up System

A fast, simple web application for F3 workout groups to manage volunteer workout leaders (Qs). Built with speed and simplicity as the top priorities.

## Features

### For PAX (Members)
- **Lightning-fast schedule view** - See weekly workout schedule at a glance
- **Quick Q sign-up** - Sign up to lead in under 30 seconds
- **Visual gap indicators** - Empty slots are prominently highlighted
- **Email reminders** - Get reminded 2 days before your Q (optional)
- **Mobile-first design** - Optimized for phone use

### For Admins
- **Coverage statistics** - See how many workouts are covered
- **Location management** - Add, edit, and manage workout locations
- **Workout schedule management** - Configure recurring workouts
- **Q signup management** - View and manage all Q assignments
- **Email notifications** - SMTP configuration for automated reminders
- **Simple authentication** - Shared password for sign-ups, separate admin password

### Technical Highlights
- **Fast page loads** - Under 1 second on mobile networks
- **Minimal JavaScript** - Uses HTMX for interactivity
- **SQLite database** - No separate database server needed
- **Easy deployment** - Docker-based with docker-compose
- **Notification API** - JSON endpoints for integrations (Slack, etc.)

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd q-sheet

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Build and run with Docker
docker-compose up -d

# Import sample F3 Cherokee data
docker exec -it f3-qsheet python import_f3_data.py

# Access the application
open http://localhost:5000
```

### Option 2: Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python database.py

# Import sample data
python import_f3_data.py

# Run development server
python app.py

# Access at http://localhost:5000
```

## Configuration

Edit `.env` file with your settings:

```bash
# Flask Configuration
SECRET_KEY=your-random-secret-key-here
FLASK_ENV=production

# Database
DATABASE_PATH=qsheet.db

# Application Settings
REGION_NAME=F3 Cherokee
SIGNUP_WINDOW_DAYS=90
REMINDER_DAYS_BEFORE=2

# Passwords (CHANGE THESE!)
SIGNUP_PASSWORD=f3cherokee
ADMIN_PASSWORD=admin123

# SMTP Email (optional)
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=F3 Q-Sheet
```

## Default Credentials

**Sign-Up Password:** `f3cherokee` (shared by all PAX)
**Admin Password:** `admin123` (CHANGE THIS!)

Access admin panel at: http://localhost:5000/admin/login

## Data Import

### Import Sample Data

```bash
python import_f3_data.py
```

### Import from CSV

Create a CSV file with columns: Location,Address,Day,Time,Type

```bash
python import_f3_data.py --csv your_data.csv
```

### Manual Import via Admin Panel

1. Login to admin panel
2. Go to "Manage Locations"
3. Add locations one by one
4. Go to "Manage Workouts"
5. Add workout schedules for each location

## Email Notifications

### Setup SMTP

Configure SMTP settings in `.env` or via admin settings panel.

For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the app password in `SMTP_PASSWORD`

### Send Test Reminder

```bash
python email_notifications.py
```

### Automated Reminders

Set up a daily cron job:

```bash
# Run at 8 AM daily
0 8 * * * cd /path/to/qsheet && python email_notifications.py
```

Or use the Docker cron service (uncomment in docker-compose.yml).

## API Endpoints

### Notification API

Get recent signups (for Slack/webhooks):
```bash
GET /api/notifications/recent?hours=24
```

Get upcoming workouts needing reminders:
```bash
GET /api/notifications/upcoming?days=2
```

Create signup via API:
```bash
POST /api/signup
Content-Type: application/json

{
  "workout_id": 1,
  "date": "2024-01-15",
  "q_name": "Squeegee",
  "q_email": "squeegee@f3.com",
  "password": "f3cherokee",
  "notes": "Gonna be a beatdown!"
}
```

## Database Backup

### SQLite Backup

```bash
# Backup
cp data/qsheet.db data/qsheet.db.backup

# Restore
cp data/qsheet.db.backup data/qsheet.db
```

### Automated Backup Script

```bash
# Daily backup at midnight
0 0 * * * cp /path/to/qsheet/data/qsheet.db /path/to/backups/qsheet-$(date +\%Y\%m\%d).db
```

## Production Deployment

### Requirements
- Server with Docker and docker-compose
- Domain name (optional, but recommended)
- SSL certificate (Let's Encrypt recommended)

### Steps

1. **Set up server** (Ubuntu/Debian example)
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl enable docker
```

2. **Clone and configure**
```bash
cd /opt
sudo git clone <repository-url> qsheet
cd qsheet
sudo cp .env.example .env
sudo nano .env  # Edit with production settings
```

3. **Generate secure secret key**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy output to SECRET_KEY in .env
```

4. **Change default passwords**
Edit `.env` and change:
- `SIGNUP_PASSWORD`
- `ADMIN_PASSWORD`

5. **Start application**
```bash
sudo docker-compose up -d
```

6. **Import data**
```bash
sudo docker exec -it f3-qsheet python import_f3_data.py
```

7. **Set up nginx reverse proxy** (optional)
See `nginx.conf.example` for configuration

8. **Set up SSL** with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Multi-Region Setup

To run multiple regions on one server:

1. Copy the entire directory for each region
2. Change ports in docker-compose.yml
3. Use nginx to route by subdomain

Example:
- `cherokee.f3qsheet.com` → Port 5000
- `atlanta.f3qsheet.com` → Port 5001

## Performance Optimization

The application is already optimized for speed:

- **SQLite WAL mode** - Better concurrent access
- **Efficient queries** - Indexed lookups
- **CDN assets** - Tailwind and HTMX from CDN
- **Static file caching** - 1-year cache headers
- **Minimal dependencies** - Fast startup

For higher traffic:
- Use nginx for static file serving
- Enable gzip compression
- Increase gunicorn workers
- Consider PostgreSQL for very high traffic

## Troubleshooting

### Database locked errors
```bash
# Restart the application
docker-compose restart
```

### Can't access on mobile
```bash
# Make sure firewall allows port 5000
sudo ufw allow 5000
```

### Email not sending
1. Check SMTP settings in `.env`
2. For Gmail, use App Password, not regular password
3. Test with: `python email_notifications.py`

### Password not working
Passwords are case-sensitive. Check:
1. `.env` file settings
2. Admin panel → Settings

## Technology Stack

- **Backend:** Python 3.11 + Flask
- **Database:** SQLite 3 (with WAL mode)
- **Frontend:** HTMX + Tailwind CSS (CDN)
- **Server:** Gunicorn
- **Container:** Docker + docker-compose

## Development

### Project Structure

```
q-sheet/
├── app.py                  # Main Flask application
├── models.py              # Database models and queries
├── database.py            # Database connection and utilities
├── config.py              # Configuration management
├── schema.sql             # Database schema
├── import_f3_data.py      # Data import script
├── email_notifications.py # Email system
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── signup.html
│   └── admin/
└── static/              # Static assets
    ├── css/
    └── js/
```

## License

MIT License - Feel free to use for your F3 region!

## Support

For issues, questions, or feature requests, open an issue on GitHub.

## Credits

Built for F3 Cherokee with speed and simplicity in mind.

**F3 Mission:** Plant, Grow, and Serve Small Workout Groups for Men