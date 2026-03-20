import os
import sqlite3

base_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_path, "../", "data", "database.db")


def insert_project(project_id, project_name, description,
                   coordinator, start_date, end_date):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO projects (
                project_id, project_name, description,
                coordinator, start_date, end_date
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (project_id, project_name, description,
             coordinator, start_date, end_date)
        )
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def list_projects():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
