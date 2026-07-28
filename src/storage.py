import json
import os
import time
from typing import Any

def _db_path() -> str:
    # database directory placed in repo root/database
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base, "database", "data.json")

def append_analysis(record: dict[str, Any]) -> str:
    path = _db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # add a timestamp so each entry is traceable
    record["_saved_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    data.append(record)

    # atomic write
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, path)
    return path
