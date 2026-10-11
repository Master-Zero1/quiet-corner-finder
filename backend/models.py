"""
Database models and initialization for Quiet Corner Finder.
SQLite schema matches PRD specifications:
- spaces
- space_attributes (EAV store for Constraint 1 flexibility)
- opening_hours
- reports (with predicted_noise, device_hash, and outlier dampening)
"""
import sqlite3
import config

NOISE_LEVELS = {
    1: "Quiet",
    2: "Moderate",
    3: "Loud"
}

CROWD_LEVELS = {
    1: "Empty",
    2: "Some seats",
    3: "Crowded"
}

def get_db(db_path=None):
    """Returns a SQLite connection with row access by column name."""
    path = db_path or config.DATABASE
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path=None):
    """Initializes the database schema and indexes."""
    conn = get_db(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS spaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        building TEXT NOT NULL,
        lat REAL,
        lng REAL,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS space_attributes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        space_id INTEGER NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        UNIQUE(space_id, key)
    );

    CREATE TABLE IF NOT EXISTS opening_hours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        space_id INTEGER NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
        weekday INTEGER NOT NULL, -- 0=Monday ... 6=Sunday (ISO format)
        open_time TEXT NOT NULL,   -- "HH:MM"
        close_time TEXT NOT NULL   -- "HH:MM"
    );

    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        space_id INTEGER NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
        noise INTEGER NOT NULL,    -- 1=Quiet, 2=Moderate, 3=Loud
        crowd INTEGER NOT NULL,    -- 1=Empty, 2=Some seats, 3=Crowded
        created_at TEXT NOT NULL,  -- ISO 8601 UTC string: YYYY-MM-DDTHH:MM:SSZ
        device_hash TEXT NOT NULL, -- SHA-256 hash of device token
        predicted_noise INTEGER,   -- Snapshot of what UI showed before submission (1, 2, or 3)
        is_outlier INTEGER DEFAULT 0 -- Flag for consensus deviation
    );

    -- Performance indexes for time decay and attribute queries
    CREATE INDEX IF NOT EXISTS idx_reports_space_created ON reports(space_id, created_at);
    CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at);
    CREATE INDEX IF NOT EXISTS idx_reports_device ON reports(device_hash, space_id, created_at);
    CREATE INDEX IF NOT EXISTS idx_attributes_space_key ON space_attributes(space_id, key);
    CREATE INDEX IF NOT EXISTS idx_hours_space_day ON opening_hours(space_id, weekday);
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
