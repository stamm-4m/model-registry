import sqlite3
import os

base_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_path, "../", "data", "database.db")



def init_db():
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # ---- USERS TABLE ----
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # ---- PROJECTS TABLE ----
    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY,
        project_name TEXT NOT NULL,
        description TEXT,
        coordinator TEXT,
        start_date TEXT,
        end_date TEXT
    )
    """)

    # ---- USER ↔ PROJECT RELATION TABLE ----
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_projects (
        user_id INTEGER NOT NULL,
        project_id TEXT NOT NULL,
        can_access INTEGER DEFAULT 1,
        PRIMARY KEY (user_id, project_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
