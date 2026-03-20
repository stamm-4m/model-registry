import os
import sqlite3

base_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_path, "../", "data", "database.db")


def assign_user_to_project(user_id, project_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO user_projects
        (user_id, project_id, can_access)
        VALUES (?, ?, 1)
        """,
        (user_id, project_id)
    )

    conn.commit()
    conn.close()


def list_projects_for_user(user_id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT p.project_id, p.project_name
        FROM projects p
        JOIN user_projects up ON p.project_id = up.project_id
        WHERE up.user_id = ? AND up.can_access = 1
        """,
        (user_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
