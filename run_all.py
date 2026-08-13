import os
import subprocess
import sys
import venv
from pathlib import Path

REQUIRED_PACKAGES = ["pygame"]
PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"

if sys.platform == "win32":
    VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
    VENV_PIP = VENV_DIR / "Scripts" / "pip.exe"
else:
    VENV_PYTHON = VENV_DIR / "bin" / "python"
    VENV_PIP = VENV_DIR / "bin" / "pip"


def is_in_venv():
    return sys.prefix == str(VENV_DIR)


def bootstrap_and_run():
    if not VENV_DIR.exists():
        print(f"[+] Creating virtual environment at {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)

    print("[+] Installing required packages...")
    subprocess.check_call([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([str(VENV_PYTHON), "-m", "pip", "install", *REQUIRED_PACKAGES])

    print("[+] Launching coding platformer...\n" + "=" * 60)
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(PROJECT_ROOT / "main.py")])


def main():
    if not is_in_venv():
        bootstrap_and_run()
    else:
        os.execv(sys.executable, [sys.executable, str(PROJECT_ROOT / "main.py")])


if __name__ == "__main__":
    main()
