import json
from pathlib import Path
from src.config.settings import METADATA_DIR

def _path(name: str) -> Path:
    # Only internally generated JSON identifiers should be used here.
    if name not in {"files", "requests", "demo_keys", "demo_users"}:
        raise ValueError("Unsupported metadata collection")
    return METADATA_DIR / f"{name}.json"

def read_collection(name: str) -> list[dict]:
    path = _path(name)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))

def write_collection(name: str, records: list[dict]) -> None:
    path = _path(name)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(records, indent=2), encoding="utf-8")
    temp.replace(path)
