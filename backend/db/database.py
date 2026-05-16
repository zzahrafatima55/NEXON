import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'movies.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT,
            google_id   TEXT UNIQUE,
            avatar      TEXT,
            bio         TEXT DEFAULT '',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS watchlist (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            movie_id    TEXT,
            title       TEXT,
            poster      TEXT,
            rating      REAL,
            year        TEXT,
            overview    TEXT,
            added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, movie_id)
        );

        CREATE TABLE IF NOT EXISTS watch_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            movie_id    TEXT,
            title       TEXT,
            poster      TEXT,
            user_rating INTEGER,
            overview    TEXT,
            watched_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # add bio column if it doesn't exist (for existing DBs)
    try:
        conn.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass
    conn.close()
    print("✅ Database ready")