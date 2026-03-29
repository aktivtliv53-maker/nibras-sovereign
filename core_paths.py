import os
import json
from pathlib import Path

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))

def load_json(relative_path):
    full_path = BASE_DIR / relative_path
    if not full_path.exists():
        raise FileNotFoundError(f"❌ الملف غير موجود: {full_path}")
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)

def debug_paths():
    files = []
    for root, dirs, fs in os.walk(BASE_DIR):
        for f in fs:
            files.append(str(Path(root) / f))
    return files
