import json
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any

DATA_FILE = Path(__file__).parent.parent / "expenses.json"
UNDO_FILE = Path(__file__).parent.parent / ".expenses_undo.json"

CATEGORIES = [
    "food", "transport", "housing", "utilities", "health",
    "entertainment", "shopping", "education", "travel", "other",
]


def load_data() -> list[dict]:
    """Load expenses from JSON file."""
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            raise ValueError("Root JSON element must be a list.")
        return data
    except json.JSONDecodeError as exc:
        raise ValueError(f"{DATA_FILE.name} is not valid JSON — {exc}")
    except (OSError, PermissionError) as exc:
        raise ValueError(f"cannot read {DATA_FILE.name} — {exc}")
    except ValueError as exc:
        raise ValueError(str(exc))


def _atomic_write(path: Path, data: Any) -> None:
    """Write data to path atomically via tempfile + os.replace."""
    try:
        fd, tmp = tempfile.mkstemp(suffix=".tmp", dir=path.parent, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            os.replace(tmp, path)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
    except (OSError, PermissionError) as exc:
        raise ValueError(f"cannot save data — {exc}")


def save_data(expenses: list[dict]) -> None:
    """Save expenses to JSON file atomically."""
    _atomic_write(DATA_FILE, expenses)


def save_undo(snapshot: list[dict], action: str) -> None:
    """Save undo snapshot atomically."""
    _atomic_write(UNDO_FILE, {"action": action, "snapshot": snapshot})


def load_undo() -> Optional[dict]:
    """Load undo snapshot if it exists."""
    if not UNDO_FILE.exists():
        return None
    try:
        with UNDO_FILE.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def clear_undo() -> None:
    """Delete undo file."""
    UNDO_FILE.unlink(missing_ok=True)


def next_id(expenses: list[dict]) -> int:
    """Get next available ID."""
    return max((e.get("id", 0) for e in expenses), default=0) + 1


def val_amount(value: str) -> float:
    """Validate and convert amount."""
    try:
        amt = float(value)
    except ValueError:
        raise ValueError(f"amount must be a number, got '{value}'.")
    if amt <= 0:
        raise ValueError("amount must be greater than zero.")
    return round(amt, 2)


def val_date(value: str, field: str = "date") -> str:
    """Validate date format."""
    try:
        from datetime import datetime
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise ValueError(f"{field} must be YYYY-MM-DD, got '{value}'.")


def val_category(value: str) -> str:
    """Validate category."""
    cat = value.strip().lower()
    if cat not in CATEGORIES:
        raise ValueError(f"unknown category '{cat}'. Valid: {', '.join(CATEGORIES)}")
    return cat


def apply_filters(expenses: list[dict], category: Optional[str] = None,
                  from_date: Optional[str] = None, to_date: Optional[str] = None,
                  last: Optional[int] = None) -> list[dict]:
    """Apply filters to expenses list."""
    result = list(expenses)
    
    if category:
        cat = val_category(category)
        result = [e for e in result if e["category"] == cat]
    
    if from_date:
        fd = val_date(from_date, "from_date")
        result = [e for e in result if e["date"] >= fd]
    
    if to_date:
        td = val_date(to_date, "to_date")
        result = [e for e in result if e["date"] <= td]
    
    result = sorted(result, key=lambda e: (e["date"], e["id"]))
    
    if last:
        result = result[-last:]
    
    return result
