-- F3 Q-Sheet Database Schema
-- Optimized for speed and simplicity

-- Locations table (AO = Area of Operation in F3 terminology)
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    address TEXT NOT NULL,
    region TEXT DEFAULT 'Cherokee',
    latitude REAL,
    longitude REAL,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workouts table (recurring schedule)
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0=Sunday, 1=Monday, ..., 6=Saturday
    time TEXT NOT NULL, -- Format: "HH:MM" (24-hour)
    workout_type TEXT DEFAULT 'Boot Camp', -- Boot Camp, Run, Ruck, etc.
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE,
    UNIQUE(location_id, day_of_week, time)
);

-- Q Sign-ups table (actual assignments to specific dates)
CREATE TABLE IF NOT EXISTS q_signups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    date DATE NOT NULL, -- Specific date for the workout (YYYY-MM-DD)
    q_name TEXT NOT NULL,
    q_email TEXT, -- Optional for reminders
    notes TEXT, -- Optional notes from Q
    reminded BOOLEAN DEFAULT 0, -- Whether reminder email was sent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE,
    UNIQUE(workout_id, date) -- Only one Q per workout per date
);

-- Settings table (key-value store for configuration)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_workouts_location ON workouts(location_id);
CREATE INDEX IF NOT EXISTS idx_workouts_day ON workouts(day_of_week);
CREATE INDEX IF NOT EXISTS idx_signups_workout ON q_signups(workout_id);
CREATE INDEX IF NOT EXISTS idx_signups_date ON q_signups(date);
CREATE INDEX IF NOT EXISTS idx_signups_reminded ON q_signups(reminded);
CREATE INDEX IF NOT EXISTS idx_locations_active ON locations(active);
CREATE INDEX IF NOT EXISTS idx_workouts_active ON workouts(active);

-- Default settings
INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('signup_password', 'f3cherokee', 'Shared password for Q sign-ups'),
    ('admin_password', 'admin123', 'Admin interface password (CHANGE THIS!)'),
    ('region_name', 'F3 Cherokee', 'Region branding name'),
    ('signup_window_days', '90', 'How many days ahead people can sign up'),
    ('reminder_days_before', '2', 'Days before workout to send reminder'),
    ('smtp_enabled', '0', 'Enable email notifications'),
    ('smtp_host', '', 'SMTP server hostname'),
    ('smtp_port', '587', 'SMTP server port'),
    ('smtp_username', '', 'SMTP authentication username'),
    ('smtp_password', '', 'SMTP authentication password'),
    ('smtp_from_email', '', 'From email address'),
    ('smtp_from_name', 'F3 Q-Sheet', 'From display name');

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_locations_timestamp
    AFTER UPDATE ON locations
BEGIN
    UPDATE locations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_workouts_timestamp
    AFTER UPDATE ON workouts
BEGIN
    UPDATE workouts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_signups_timestamp
    AFTER UPDATE ON q_signups
BEGIN
    UPDATE q_signups SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_settings_timestamp
    AFTER UPDATE ON settings
BEGIN
    UPDATE settings SET updated_at = CURRENT_TIMESTAMP WHERE key = NEW.key;
END;
