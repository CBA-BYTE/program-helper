import json
import sqlite3
from pathlib import Path


class DatabaseService:
    def __init__(self, db_path="game_save.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS student_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT UNIQUE,
                xp INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 1
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS command_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                level_id INTEGER,
                command_entered TEXT,
                was_successful INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES student_profile(id)
            )
            """
        )
        self.conn.commit()

    def get_or_create_student(self, name: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, xp, current_level FROM student_profile WHERE student_name = ?",
            (name,),
        )
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "xp": row[1], "level": row[2]}

        cursor.execute("INSERT INTO student_profile (student_name) VALUES (?)", (name,))
        self.conn.commit()
        return {"id": cursor.lastrowid, "xp": 0, "level": 1}

    def log_command(self, student_id: int, level_id: int, command: str, success: bool):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO command_logs (student_id, level_id, command_entered, was_successful)
            VALUES (?, ?, ?, ?)
            """,
            (student_id, level_id, command, 1 if success else 0),
        )
        self.conn.commit()

    def add_xp(self, student_id: int, amount: int):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE student_profile SET xp = xp + ? WHERE id = ?", (amount, student_id))
        self.conn.commit()

    def export_teacher_report(self, file_path="teacher_report.json"):
        """Exports student metrics and command histories to JSON for teacher review."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT s.student_name, s.xp, s.current_level, l.command_entered, l.was_successful, l.timestamp
            FROM student_profile s
            LEFT JOIN command_logs l ON s.id = l.student_id
            """
        )
        rows = cursor.fetchall()

        report = {}
        for row in rows:
            name, xp, level, cmd, success, time = row
            if name not in report:
                report[name] = {"xp": xp, "level": level, "history": []}
            if cmd:
                report[name]["history"].append(
                    {"command": cmd, "success": bool(success), "timestamp": time}
                )

        output_path = Path(file_path)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=4)

        return str(output_path.resolve())
