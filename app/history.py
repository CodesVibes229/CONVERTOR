import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def add_history(entry):
    history = load_history()
    entry["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(entry)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
