#!/usr/bin/env python3
"""
expenses.py  v3.1  — Collaborative edition (Claude + Grok)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Positional args · Atomic JSON · Specific exceptions
TTY-safe colour · Dual bar charts · Monthly rollup
Category validation · ls/rm/bd aliases · --last N · undo

Commands:
  add   <amount> <category> [--date YYYY-MM-DD] [--note TEXT]
  list  (alias: ls)  [--category CAT] [--from DATE] [--to DATE] [--last N]
  breakdown (alias: bd)  [--from DATE] [--to DATE]
  monthly              [--from DATE] [--to DATE]
  delete <id> (alias: rm <id>)
  undo                 — reverse the last add or delete
  categories           — show valid category names
"""

import argparse
import json
import sys
import tempfile
import os
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

DATA_FILE  = Path(__file__).parent / "expenses.json"
UNDO_FILE  = Path(__file__).parent / ".expenses_undo.json"   # single-step undo

# ── Categories ────────────────────────────────────────────────────────────────

CATEGORIES = [
    "food", "transport", "housing", "utilities", "health",
    "entertainment", "shopping", "education", "travel", "other",
]

# ── TTY-safe colour (honours NO_COLOR standard) ───────────────────────────────

_USE_COLOUR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text

RED     = lambda t: _c("31", t)
GREEN   = lambda t: _c("32", t)
YELLOW  = lambda t: _c("33", t)
CYAN    = lambda t: _c("36", t)
MAGENTA = lambda t: _c("35", t)
BOLD    = lambda t: _c("1",  t)
DIM     = lambda t: _c("2",  t)

# ── Storage ───────────────────────────────────────────────────────────────────

def load_data() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            raise ValueError("Root JSON element must be a list.")
        return data
    except json.JSONDecodeError as exc:
        sys.exit(RED(f"Error: {DATA_FILE.name} is not valid JSON — {exc}"))
    except (OSError, PermissionError) as exc:
        sys.exit(RED(f"Error: cannot read {DATA_FILE.name} — {exc}"))
    except ValueError as exc:
        sys.exit(RED(f"Error: {exc}"))


def _atomic_write(path: Path, data: list[dict]) -> None:
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
        sys.exit(RED(f"Error: cannot save data — {exc}"))


def save_data(expenses: list[dict]) -> None:
    _atomic_write(DATA_FILE, expenses)


def save_undo(snapshot: list[dict], action: str) -> None:
    _atomic_write(UNDO_FILE, {"action": action, "snapshot": snapshot})


def load_undo() -> dict | None:
    if not UNDO_FILE.exists():
        return None
    try:
        with UNDO_FILE.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def clear_undo() -> None:
    UNDO_FILE.unlink(missing_ok=True)


def next_id(expenses: list[dict]) -> int:
    return max((e.get("id", 0) for e in expenses), default=0) + 1

# ── Validation ────────────────────────────────────────────────────────────────

def val_amount(value: str) -> float:
    try:
        amt = float(value)
    except ValueError:
        sys.exit(RED(f"Error: amount must be a number, got '{value}'."))
    if amt <= 0:
        sys.exit(RED("Error: amount must be greater than zero."))
    return round(amt, 2)


def val_date(value: str, field: str = "--date") -> str:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        sys.exit(RED(f"Error: {field} must be YYYY-MM-DD, got '{value}'."))


def val_category(value: str) -> str:
    cat = value.strip().lower()
    if cat not in CATEGORIES:
        sys.exit(
            RED(f"Error: unknown category '{cat}'.\n")
            + f"       Valid: {', '.join(CATEGORIES)}"
        )
    return cat


def apply_filters(expenses: list[dict], args: argparse.Namespace) -> list[dict]:
    result = list(expenses)
    if getattr(args, "category", None):
        cat = val_category(args.category)
        result = [e for e in result if e["category"] == cat]
    if getattr(args, "from_date", None):
        fd = val_date(args.from_date, "--from")
        result = [e for e in result if e["date"] >= fd]
    if getattr(args, "to_date", None):
        td = val_date(args.to_date, "--to")
        result = [e for e in result if e["date"] <= td]
    result = sorted(result, key=lambda e: (e["date"], e["id"]))
    if getattr(args, "last", None):
        result = result[-args.last:]
    return result

# ── Display helpers ───────────────────────────────────────────────────────────

def _bar_pct(pct: float, width: int = 20) -> str:
    """Fixed-scale bar: each block = 2.5% of total."""
    filled = min(int(pct / 2.5), width)
    return CYAN("█" * filled) + DIM("░" * (width - filled))


def _bar_prop(amt: float, peak: float, width: int = 20) -> str:
    """Proportional bar: tallest bar fills width."""
    filled = int(amt / peak * width) if peak else 0
    return CYAN("█" * filled)


def _print_table(expenses: list[dict]) -> None:
    print()
    print(BOLD(f"  {'ID':>4}  {'Amount':>9}  {'Category':<14}  {'Date':<10}  Note"))
    print(DIM("  " + "─" * 62))
    for e in expenses:
        raw = e.get("note") or ""
        note = raw[:40] + "…" if len(raw) > 40 else raw
        print(
            f"  {BOLD('#')}{e['id']:>4}  "
            + CYAN(f"${e['amount']:>8.2f}")
            + f"  {e['category']:<14}  {e['date']}  "
            + DIM(note)
        )
    print()


def _range_label(expenses: list[dict]) -> str:
    dates = sorted(e["date"] for e in expenses)
    return dates[0] if dates[0] == dates[-1] else f"{dates[0]} → {dates[-1]}"

# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_add(args: argparse.Namespace) -> None:
    amount   = val_amount(args.amount)
    category = val_category(args.category)
    exp_date = val_date(args.date, "--date") if args.date else date.today().isoformat()
    note     = (args.note or "").strip()

    expenses = load_data()
    save_undo(expenses, "add")                      # snapshot before change

    entry = {
        "id":       next_id(expenses),
        "amount":   amount,
        "category": category,
        "date":     exp_date,
        "note":     note,
    }
    expenses.append(entry)
    save_data(expenses)

    print(
        GREEN("✔ Added") + f"  #{entry['id']:>4}  "
        + CYAN(f"${amount:>9.2f}")
        + f"  {category:<14}  {exp_date}"
        + (DIM(f"  {note}") if note else "")
    )


def cmd_list(args: argparse.Namespace) -> None:
    expenses = load_data()
    if not expenses:
        print(DIM("No expenses recorded yet.")); return

    filtered = apply_filters(expenses, args)
    if not filtered:
        print(YELLOW("No expenses match the given filters.")); return

    _print_table(filtered)
    total = sum(e["amount"] for e in filtered)
    print(DIM("  " + "─" * 62))
    print(f"  {' ':>40}  {BOLD('Total')}  {BOLD(CYAN(f'${total:>9.2f}'))}")
    print()


def cmd_breakdown(args: argparse.Namespace) -> None:
    expenses = load_data()
    if not expenses:
        print(DIM("No expenses recorded yet.")); return

    filtered = apply_filters(expenses, args)
    if not filtered:
        print(YELLOW("No expenses match the given filters.")); return

    total = sum(e["amount"] for e in filtered)
    by_cat: dict[str, float] = defaultdict(float)
    for e in filtered:
        by_cat[e["category"]] += e["amount"]

    print()
    print(BOLD("  Category Breakdown"))
    print(DIM(f"  {_range_label(filtered)}  ·  {len(filtered)} entries"))
    print(DIM("  " + "─" * 62))
    print(BOLD(f"  {'Category':<14}  {'Amount':>9}  {'Share':>6}  {'':20}"))
    print(DIM("  " + "─" * 62))

    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = amt / total * 100
        print(f"  {cat:<14}  {CYAN(f'${amt:>8.2f}')}  {pct:>5.1f}%  {_bar_pct(pct)}")

    print(DIM("  " + "─" * 62))
    print(f"  {'TOTAL':<14}  {BOLD(CYAN(f'${total:>8.2f}'))}")
    print()


def cmd_monthly(args: argparse.Namespace) -> None:
    expenses = load_data()
    if not expenses:
        print(DIM("No expenses recorded yet.")); return

    filtered = apply_filters(expenses, args)
    if not filtered:
        print(YELLOW("No expenses match the given filters.")); return

    by_month: dict[str, float] = defaultdict(float)
    for e in filtered:
        by_month[e["date"][:7]] += e["amount"]

    grand = sum(by_month.values())
    peak  = max(by_month.values())

    print()
    print(BOLD("  Monthly Totals"))
    print(DIM(f"  {_range_label(filtered)}  ·  {len(filtered)} entries"))
    print(DIM("  " + "─" * 52))

    for month in sorted(by_month, reverse=True):
        amt = by_month[month]
        pct = amt / grand * 100
        print(
            f"  {MAGENTA(month)}  {CYAN(f'${amt:>9.2f}')}  {pct:>5.1f}%  "
            + _bar_prop(amt, peak)
        )

    print(DIM("  " + "─" * 52))
    print(f"  {'TOTAL':<7}  {BOLD(CYAN(f'${grand:>9.2f}'))}")
    print()


def cmd_delete(args: argparse.Namespace) -> None:
    try:
        target = int(args.id)
    except ValueError:
        sys.exit(RED(f"Error: id must be an integer, got '{args.id}'."))

    expenses = load_data()
    idx = next((i for i, e in enumerate(expenses) if e.get("id") == target), None)
    if idx is None:
        sys.exit(RED(f"Error: no expense with id {target}."))

    save_undo(expenses, "delete")                   # snapshot before change
    entry = expenses.pop(idx)
    save_data(expenses)

    print(
        RED("✖ Deleted") + f"  #{entry['id']:>4}  "
        + CYAN(f"${entry['amount']:>9.2f}")
        + f"  {entry['category']:<14}  {entry['date']}"
        + (DIM(f"  {entry['note']}") if entry.get("note") else "")
    )


def cmd_undo(_args: argparse.Namespace) -> None:
    """Restore the data file to its state before the last add or delete."""
    undo = load_undo()
    if not undo:
        print(YELLOW("Nothing to undo.")); return

    save_data(undo["snapshot"])
    clear_undo()               # one-shot — can't undo an undo
    print(GREEN(f"✔ Undid last {undo['action']}.") + DIM("  (undo history cleared)"))


def cmd_categories(_args: argparse.Namespace) -> None:
    print(BOLD("\n  Available categories:"))
    for cat in CATEGORIES:
        print(f"    • {cat}")
    print()

# ── Argument parser ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="expenses",
        description="CLI Expense Tracker  v3.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Aliases:  ls = list   rm = delete   bd = breakdown\n"
            "Tip:      run 'categories' to see valid category names.\n"
            "Undo:     one-step undo after any add or delete."
        ),
    )
    sub = root.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    def _date_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--from", metavar="YYYY-MM-DD", dest="from_date", help="Start date (inclusive)")
        p.add_argument("--to",   metavar="YYYY-MM-DD", dest="to_date",   help="End date (inclusive)")

    # ── add ──
    p = sub.add_parser("add", help="Record a new expense.")
    p.add_argument("amount",   help="Amount, e.g. 12.50")
    p.add_argument("category", help="Category (see 'categories')")
    p.add_argument("--date",   metavar="YYYY-MM-DD", help="Date (default: today)")
    p.add_argument("--note",   metavar="TEXT",       help="Optional note")
    p.set_defaults(func=cmd_add)

    # ── list / ls ──
    for alias in ("list", "ls"):
        p = sub.add_parser(alias,
                           help="List expenses." if alias == "list" else None,
                           add_help=alias == "list")
        p.add_argument("--category", "-c", metavar="CAT",  help="Filter by category")
        p.add_argument("--last",     "-n", metavar="N", type=int, help="Show only the last N entries")
        _date_args(p)
        p.set_defaults(func=cmd_list)

    # ── breakdown / bd ──
    for alias in ("breakdown", "bd"):
        p = sub.add_parser(alias,
                           help="Category breakdown with percentages." if alias == "breakdown" else None,
                           add_help=alias == "breakdown")
        _date_args(p)
        p.set_defaults(func=cmd_breakdown)

    # ── monthly ──
    p = sub.add_parser("monthly", help="Monthly spending rollup.")
    _date_args(p)
    p.set_defaults(func=cmd_monthly)

    # ── delete / rm ──
    for alias in ("delete", "rm"):
        p = sub.add_parser(alias,
                           help="Delete an expense by ID." if alias == "delete" else None,
                           add_help=alias == "delete")
        p.add_argument("id", help="Expense ID")
        p.set_defaults(func=cmd_delete)

    # ── undo ──
    p = sub.add_parser("undo", help="Undo the last add or delete.")
    p.set_defaults(func=cmd_undo)

    # ── categories ──
    p = sub.add_parser("categories", help="List valid category names.")
    p.set_defaults(func=cmd_categories)

    return root


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
