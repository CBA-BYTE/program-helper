import os
import subprocess
import sys
import venv
from pathlib import Path

PRIMARY_PACKAGE = "pygame"
FALLBACK_PACKAGE = "pygame-ce"
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


def _run_pip(*args: str):
    subprocess.check_call([str(VENV_PYTHON), "-m", "pip", *args])


def install_graphics_runtime():
    # Prefer prebuilt wheels to avoid local C/C++ compilation on user machines.
    try:
        _run_pip("install", "--only-binary=:all:", PRIMARY_PACKAGE)
        print(f"[+] Installed {PRIMARY_PACKAGE}.")
    except subprocess.CalledProcessError:
        print(
            "[!] Could not install pygame wheel for this Python version. "
            "Trying pygame-ce as a compatible fallback..."
        )
        _run_pip("install", "--only-binary=:all:", FALLBACK_PACKAGE)
        print(f"[+] Installed {FALLBACK_PACKAGE}.")


def bootstrap():
    if not VENV_DIR.exists():
        print(f"[+] Creating virtual environment at {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)

    print("[+] Validating dependencies...")
    _run_pip("install", "--upgrade", "pip", "setuptools", "wheel")
    install_graphics_runtime()

    print("[+] Launching advanced game...\n" + "=" * 60)
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(PROJECT_ROOT / "main.py")])


if __name__ == "__main__":
    if not is_in_venv():
        bootstrap()
    else:
        os.execv(sys.executable, [sys.executable, str(PROJECT_ROOT / "main.py")])
