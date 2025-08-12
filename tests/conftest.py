import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "stubs"))
sys.path.insert(0, str(BASE_DIR.parent))
