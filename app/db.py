"""SQLite persistence layer."""
import os, sqlite3
from contextlib import contextmanager
from passlib.hash import bcrypt

DB_PATH = os.path.join("data", "app.db")

def _conn():
    os.makedirs("data", exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

@contextmanager
def cursor():
    c = _conn()
    try:
        yield c.cursor()
        c.commit()
    finally:
        c.close()

def init_db():
    with cursor() as cur:
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            email_verified INTEGER DEFAULT 0,
            phone_verified INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS scans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            kind TEXT,
            input_preview TEXT,
            score INTEGER,
            level TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS incidents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            severity TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
    # Seed admin
    with cursor() as cur:
        cur.execute("SELECT 1 FROM users WHERE email=?", ("admin@system.local",))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users(email,phone,password_hash,email_verified,phone_verified,is_admin) VALUES(?,?,?,1,1,1)",
                ("admin@system.local", "+10000000000", bcrypt.hash("Admin@123")),
            )
