import sqlite3

from code_engine import CodeEngine, ExecutionResult
from database import DatabaseService


def test_code_engine_python_execution_and_sql():
    engine = CodeEngine()
    game_objects = {"player": type("Player", (), {"x": 10, "move_right": lambda self, steps=1: setattr(self, "x", self.x + steps)})(), "door": type("Door", (), {"is_locked": True, "unlock": lambda self: setattr(self, "is_locked", False)})()}

    res = engine.execute_python_oop("player.move_right(3)\ndoor.unlock()\nprint(player.x, door.is_locked)", game_objects)
    assert res.success is True
    assert "13 False" in res.output

    sql_res = engine.execute_sql("SELECT color, is_locked FROM doors WHERE id = 1")
    assert sql_res.success is True
    assert "('red', 1)" in sql_res.output


def test_database_service_tracks_students():
    db = DatabaseService(db_path=":memory:")
    student = db.get_or_create_student("Alex")
    assert student["xp"] == 0
    db.add_xp(student["id"], 25)
    db.log_command(student["id"], 1, "door.unlock()", True)
    report_path = "teacher_report_test.json"
    db.export_teacher_report(report_path)
    assert sqlite3.connect(":memory:").execute("SELECT 1").fetchone()[0] == 1
    import os
    assert os.path.exists(report_path)
    os.remove(report_path)
