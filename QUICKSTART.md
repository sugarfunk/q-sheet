# Q-Sheet Quick Start Guide

Get F3 Q-Sheet running in 5 minutes!

## Fastest Path (Docker)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start the app
docker-compose up -d

# 3. Import sample data
docker exec -it f3-qsheet python import_f3_data.py

# 4. Open in browser
open http://localhost:5000
```

Default passwords:
- **Sign-up:** `f3cherokee`
- **Admin:** `admin123` (login at `/admin`)

## Without Docker

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env

# 4. Initialize database
python database.py

# 5. Import sample data
python import_f3_data.py

# 6. Run the app
python app.py
```

Open http://localhost:5000

## What You Get

- **Homepage** - Weekly workout schedule
- **Sign-up** - Click "NEEDS Q" to volunteer
- **Admin** - Go to `/admin` to manage everything
- **API** - JSON endpoints at `/api/*`

## Next Steps

1. **Change passwords** in `.env` file
2. **Add your locations** via admin panel
3. **Configure email** (optional) for reminders
4. **Deploy** to production server

See README.md for full documentation.

## Common Commands

```bash
# View logs (Docker)
docker-compose logs -f

# Restart (Docker)
docker-compose restart

# Backup database
cp data/qsheet.db data/qsheet.db.backup

# Import new data
python import_f3_data.py

# Send test reminders
python email_notifications.py
```

## Troubleshooting

**Port 5000 already in use?**
```bash
# Change port in docker-compose.yml
ports:
  - "8000:5000"  # Use port 8000 instead
```

**Database locked?**
```bash
docker-compose restart
```

**Need help?**
- Check README.md
- Check SETUP.md
- Open GitHub issue

That's it! Your Q-Sheet is ready to keep workouts covered!
