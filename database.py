import sqlite3
from config import DB_PATH, ADMIN_ID, ADMIN_PW


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT,
        profile TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        view_count INTEGER DEFAULT 0,
        archived INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        profile TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS likes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        profile TEXT NOT NULL,
        UNIQUE(post_id, profile)
    );

    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type TEXT NOT NULL,
        target_id INTEGER NOT NULL,
        reporter_profile TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # 관리자 계정은 고정한다.
    admin = conn.execute("SELECT 1 FROM users WHERE username=?", (ADMIN_ID,)).fetchone()
    if not admin:
        conn.execute(
            "INSERT INTO users(username, password, name, profile) VALUES(?,?,?,?)",
            (ADMIN_ID, ADMIN_PW, "관리자", "관리자"),
        )
    else:
        conn.execute(
            "UPDATE users SET password=?, profile='관리자' WHERE username=?",
            (ADMIN_PW, ADMIN_ID),
        )

    conn.commit()
    conn.close()
