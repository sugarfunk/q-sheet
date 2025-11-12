"""
Database connection and utilities
Simple SQLite connection with context manager
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from config import get_config

config = get_config()


def get_db_connection():
    """Create a database connection with optimized settings"""
    conn = sqlite3.connect(
        config.DATABASE_PATH,
        check_same_thread=False  # Allow multi-threaded access
    )
    conn.row_factory = sqlite3.Row  # Access columns by name

    # Performance optimizations
    conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging for better concurrency
    conn.execute('PRAGMA synchronous=NORMAL')  # Balance between safety and speed
    conn.execute('PRAGMA cache_size=10000')  # Larger cache for better performance
    conn.execute('PRAGMA foreign_keys=ON')  # Enable foreign key constraints

    return conn


@contextmanager
def db_transaction():
    """Context manager for database transactions"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database with schema"""
    schema_path = Path(__file__).parent / 'schema.sql'

    with open(schema_path, 'r') as f:
        schema = f.read()

    with db_transaction() as conn:
        conn.executescript(schema)

    print(f"Database initialized at {config.DATABASE_PATH}")


def get_setting(key, default=None):
    """Get a setting from the database"""
    with db_transaction() as conn:
        cursor = conn.execute(
            'SELECT value FROM settings WHERE key = ?',
            (key,)
        )
        row = cursor.fetchone()
        return row['value'] if row else default


def set_setting(key, value, description=None):
    """Set a setting in the database"""
    with db_transaction() as conn:
        if description:
            conn.execute(
                '''INSERT INTO settings (key, value, description)
                   VALUES (?, ?, ?)
                   ON CONFLICT(key) DO UPDATE SET value = ?, description = ?''',
                (key, value, description, value, description)
            )
        else:
            conn.execute(
                '''INSERT INTO settings (key, value)
                   VALUES (?, ?)
                   ON CONFLICT(key) DO UPDATE SET value = ?''',
                (key, value, value)
            )


if __name__ == '__main__':
    # Initialize database when run directly
    init_db()
