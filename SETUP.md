# F3 Q-Sheet Setup Guide

This guide will walk you through setting up F3 Q-Sheet from scratch.

## Prerequisites

Choose one of these options:

### Option A: Docker (Easiest)
- Docker installed
- Docker Compose installed
- 256MB RAM minimum
- 500MB disk space

### Option B: Local Python
- Python 3.9 or higher
- pip (Python package manager)
- 256MB RAM minimum
- 500MB disk space

## Step-by-Step Setup

### 1. Get the Code

```bash
# Clone the repository
git clone https://github.com/your-org/q-sheet.git
cd q-sheet
```

Or download and extract the ZIP file.

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the file with your settings
nano .env  # or use your favorite editor
```

**Important settings to change:**

```bash
# Generate a random secret key
SECRET_KEY=your-random-32-character-string-here

# Change default passwords
SIGNUP_PASSWORD=your-shared-password-for-pax
ADMIN_PASSWORD=your-admin-password

# Set your region name
REGION_NAME=F3 YourRegion
```

To generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3A. Docker Installation (Recommended)

```bash
# Build and start the containers
docker-compose up -d

# Check if it's running
docker-compose ps

# Initialize database and import sample data
docker exec -it f3-qsheet python database.py
docker exec -it f3-qsheet python import_f3_data.py

# View logs (optional)
docker-compose logs -f
```

Access the app at: http://localhost:5000

### 3B. Local Python Installation

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database.py

# Import sample data
python import_f3_data.py

# Run the application
python app.py
```

Access the app at: http://localhost:5000

## First Login

1. Open http://localhost:5000
2. You should see the weekly schedule (empty at first)
3. Go to http://localhost:5000/admin/login
4. Enter your admin password (from .env)
5. You're now in the admin dashboard!

## Import Your Data

### Method 1: Use Sample Data (Testing)

The sample data includes F3 Cherokee locations. This is great for testing:

```bash
python import_f3_data.py
```

### Method 2: Manual Entry (Recommended for Production)

1. Login to admin panel
2. Click "Manage Locations"
3. Add your workout locations one by one
4. Click "Manage Workouts"
5. Add workout schedules for each location

### Method 3: CSV Import (Coming Soon)

Prepare a CSV file with this format:
```csv
Location,Address,Day,Time,Type
Apex,6565 Putnam Ford Dr Woodstock GA,Monday,05:30,Boot Camp
Apex,6565 Putnam Ford Dr Woodstock GA,Thursday,05:30,Boot Camp
```

Then run:
```bash
python import_f3_data.py --csv your_data.csv
```

## Configure Email Notifications (Optional)

### Using Gmail

1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Scroll to "App passwords"
   - Generate a new app password
3. Update your `.env`:

```bash
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=F3 Q-Sheet
```

4. Restart the application
5. Test email:

```bash
python email_notifications.py
```

### Using Other Email Providers

**Outlook/Office 365:**
```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
```

**SendGrid:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

## Set Up Automated Reminders

### Linux/Mac (Cron)

```bash
# Edit crontab
crontab -e

# Add this line to run at 8 AM daily
0 8 * * * cd /path/to/qsheet && /path/to/qsheet/venv/bin/python email_notifications.py >> /path/to/logs/reminders.log 2>&1
```

### Docker (Recommended)

Uncomment the cron service in `docker-compose.yml`:

```yaml
  cron:
    build: .
    container_name: f3-qsheet-cron
    command: >
      sh -c "echo '0 8 * * * cd /app && python email_notifications.py' | crontab - && crond -f"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env:ro
    depends_on:
      - qsheet
    restart: unless-stopped
```

Then restart:
```bash
docker-compose up -d
```

## Verify Everything Works

### 1. Check Homepage
- Go to http://localhost:5000
- Should see weekly schedule
- Empty slots should be highlighted in red

### 2. Test Sign-Up Flow
- Click "NEEDS Q" on any empty slot
- Fill in name and email
- Enter signup password
- Submit
- Should see success page

### 3. Check Admin Panel
- Go to http://localhost:5000/admin
- Login with admin password
- Should see dashboard with statistics
- Try navigating to Locations, Workouts, Signups

### 4. Test API (Optional)
```bash
# Get recent signups
curl http://localhost:5000/api/notifications/recent

# Create signup via API
curl -X POST http://localhost:5000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "workout_id": 1,
    "date": "2024-12-20",
    "q_name": "Test",
    "password": "your-signup-password"
  }'
```

## Production Deployment

### For Self-Hosting

1. **Get a server** - Any VPS with 512MB RAM works
   - DigitalOcean, Linode, AWS, etc.
   - Ubuntu 22.04 LTS recommended

2. **Install Docker**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl enable docker
```

3. **Clone and configure**
```bash
cd /opt
sudo git clone <your-repo> qsheet
cd qsheet
sudo cp .env.example .env
sudo nano .env  # Configure production settings
```

4. **Start services**
```bash
sudo docker-compose up -d
```

5. **Set up domain and SSL**
```bash
# Install nginx
sudo apt install nginx

# Install certbot for SSL
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d qsheet.yourdomain.com
```

6. **Configure nginx** (see nginx.conf.example)

7. **Set up automated backups**
```bash
# Add to crontab
0 2 * * * cp /opt/qsheet/data/qsheet.db /backups/qsheet-$(date +\%Y\%m\%d).db
```

### Security Checklist for Production

- [ ] Changed SECRET_KEY to random value
- [ ] Changed SIGNUP_PASSWORD from default
- [ ] Changed ADMIN_PASSWORD from default
- [ ] Enabled HTTPS/SSL
- [ ] Set up automated backups
- [ ] Configured firewall (only 80/443 open)
- [ ] Regular updates scheduled
- [ ] Monitoring set up

## Troubleshooting

### "Database is locked" error

**Docker:**
```bash
docker-compose restart
```

**Local:**
```bash
# Kill any running Python processes
pkill -f app.py
python app.py
```

### Can't access from other devices

1. Check firewall:
```bash
sudo ufw allow 5000
```

2. Make sure you're accessing the server's IP, not localhost

### Email not sending

1. Test SMTP settings:
```bash
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print('Success!')
"
```

2. Check logs:
```bash
# Docker
docker-compose logs qsheet

# Local
tail -f app.log
```

### Import failed

Make sure database is initialized first:
```bash
python database.py
python import_f3_data.py
```

## Getting Help

1. Check the main README.md
2. Look at existing issues on GitHub
3. Open a new issue with:
   - Your setup method (Docker/Local)
   - Error messages
   - Steps to reproduce

## Next Steps

- Customize branding (logo, colors)
- Set up Slack integration
- Configure monitoring
- Train your admin team
- Roll out to your region

Congratulations! Your F3 Q-Sheet is ready to keep workouts covered!
