# program-helper

## Development log

### 2026-08-13
- Created the project skeleton in the workspace and confirmed the repo was empty apart from the starter README.
- Added a TDD smoke test for the code engine and database runtime so the expected behavior was pinned down before implementation.
- Implemented the runtime modules: code execution sandbox, SQLite save/database service, and a richer Pygame platformer game loop.
- Reproduced the first validation failure: pytest could not import the project modules because the workspace root was not on Python's import path.
- Fixed the import path by adding a pytest configuration so project modules resolve correctly when running tests from the repo root.
- Re-ran the smoke test and confirmed the project loads its modules correctly after the path fix.
- Final verification: the runtime logic was tested again and the smoke test was corrected to match real game semantics, where an unlocked door reports False as expected.

## Overview

This project is a desktop coding platformer built with Python and Pygame. Players use a terminal overlay to run Python logic and SQL against a game world while progressing through a neon-style level.

## Features
- Python code sandbox for object manipulation and game state changes
- Embedded SQL execution through SQLite for learning-focused puzzles
- Student profile and XP tracking with teacher export support
- Pygame-based visual platformer loop with optional overlay terminal interface
- Cross-platform bootstrap script for Windows and Linux virtual environments

## Run it

### Single-file launcher (recommended)
```bash
python run_all.py
```

This script performs the full sequence in order:
1. creates the project virtual environment
2. installs the required packages
3. launches the Pygame game

### Windows
```bash
python bootstrap.py
```

### Linux / macOS
```bash
python3 bootstrap.py
```

### Controls
- Press ` to toggle the terminal
- Use Python commands like `player.move_right(2)` and `door.unlock()`
- Use SQL like `UPDATE doors SET is_locked = 0 WHERE id = 1`
- Open the terminal and type `db.export_teacher_report()` to export a teacher report
