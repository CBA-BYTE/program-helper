import ast
import io
import sqlite3
import sys


class ExecutionResult:
    def __init__(self, success: bool, output: str, state_changes: dict | None = None):
        self.success = success
        self.output = output
        self.state_changes = state_changes or {}


class CodeEngine:
    def __init__(self):
        self.sql_db = sqlite3.connect(":memory:")
        self._init_sql_puzzle_db()

    def _init_sql_puzzle_db(self):
        cursor = self.sql_db.cursor()
        cursor.execute(
            "CREATE TABLE doors (id INTEGER PRIMARY KEY, color TEXT, is_locked INT)"
        )
        cursor.execute(
            "INSERT INTO doors VALUES (1, 'red', 1), (2, 'blue', 1), (3, 'green', 0)"
        )
        self.sql_db.commit()

    def execute_python_oop(self, user_code: str, game_objects: dict) -> ExecutionResult:
        """Parses and executes OOP and Python logic safely against game objects."""
        try:
            tree = ast.parse(user_code)
        except SyntaxError as exc:
            return ExecutionResult(False, f"Syntax Error: {exc}")

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return ExecutionResult(False, "Security Error: Imports are disabled in terminal.")
            if isinstance(node, ast.Name) and node.id in {
                "eval",
                "exec",
                "open",
                "__import__",
                "input",
                "compile",
                "globals",
                "locals",
                "breakpoint",
            }:
                return ExecutionResult(False, f"Security Error: '{node.id}' is restricted.")

        stdout_capture = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_capture

        safe_builtins = {
            "abs": abs,
            "bool": bool,
            "dict": dict,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "print": print,
            "range": range,
            "set": set,
            "str": str,
            "sum": sum,
            "tuple": tuple,
        }

        sandbox_scope = {**game_objects, "print": print, "__builtins__": safe_builtins}

        try:
            exec(compile(tree, "<terminal>", "exec"), sandbox_scope, sandbox_scope)
            sys.stdout = old_stdout
            output = stdout_capture.getvalue().strip()
            return ExecutionResult(True, output or "Command executed successfully.", sandbox_scope)
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            sys.stdout = old_stdout
            return ExecutionResult(False, f"Runtime Error: {type(exc).__name__} - {exc}")

    def execute_sql(self, query: str) -> ExecutionResult:
        """Executes SQL queries against the puzzle database."""
        try:
            cursor = self.sql_db.cursor()
            cursor.execute(query)

            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                return ExecutionResult(True, f"Query Result: {results}")

            self.sql_db.commit()
            return ExecutionResult(True, f"Rows affected: {cursor.rowcount}")
        except sqlite3.Error as exc:
            return ExecutionResult(False, f"SQL Error: {exc}")
