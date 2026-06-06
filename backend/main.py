import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from collections import defaultdict
from datetime import date

from models import (
    ExpenseCreate, Expense, UndoResponse,
    BreakdownResponse, CategoryTotals,
    MonthlyResponse, MonthlyTotals
)
from storage import (
    load_data, save_data, save_undo, load_undo, clear_undo,
    next_id, apply_filters, CATEGORIES
)

app = FastAPI(title="Expense Tracker API", version="3.1")

# CORS configuration
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/expenses")
def get_expenses(
    category: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    last: Optional[int] = None
):
    """Get all expenses with optional filters."""
    expenses = load_data()
    filtered = apply_filters(expenses, category, from_date, to_date, last)
    return filtered


@app.post("/api/expenses")
def add_expense(expense: ExpenseCreate):
    """Add a new expense."""
    expenses = load_data()
    save_undo(expenses, "add")
    
    entry = {
        "id": next_id(expenses),
        "amount": expense.amount,
        "category": expense.category,
        "date": expense.date,
        "note": expense.note,
    }
    expenses.append(entry)
    save_data(expenses)
    return entry


@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int):
    """Delete an expense by ID."""
    expenses = load_data()
    idx = next((i for i, e in enumerate(expenses) if e.get("id") == expense_id), None)
    
    if idx is None:
        raise HTTPException(status_code=404, detail=f"No expense with id {expense_id}")
    
    save_undo(expenses, "delete")
    entry = expenses.pop(idx)
    save_data(expenses)
    return entry


@app.post("/api/expenses/undo")
def undo_last():
    """Undo the last add or delete operation."""
    undo = load_undo()
    if not undo:
        raise HTTPException(status_code=400, detail="Nothing to undo")
    
    save_data(undo["snapshot"])
    clear_undo()
    return UndoResponse(message=f"Undid last {undo['action']}", action=undo["action"])


@app.get("/api/summary/breakdown")
def get_breakdown(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """Get category breakdown with percentages."""
    expenses = load_data()
    filtered = apply_filters(expenses, None, from_date, to_date, None)
    
    if not filtered:
        return BreakdownResponse(
            total=0.0,
            entries=0,
            range_label="",
            breakdown=[]
        )
    
    total = sum(e["amount"] for e in filtered)
    by_cat: dict[str, float] = defaultdict(float)
    for e in filtered:
        by_cat[e["category"]] += e["amount"]
    
    dates = sorted(e["date"] for e in filtered)
    range_label = dates[0] if dates[0] == dates[-1] else f"{dates[0]} → {dates[-1]}"
    
    breakdown = [
        CategoryTotals(
            category=cat,
            amount=amt,
            percentage=round(amt / total * 100, 1)
        )
        for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1])
    ]
    
    return BreakdownResponse(
        total=round(total, 2),
        entries=len(filtered),
        range_label=range_label,
        breakdown=breakdown
    )


@app.get("/api/summary/monthly")
def get_monthly(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """Get monthly totals."""
    expenses = load_data()
    filtered = apply_filters(expenses, None, from_date, to_date, None)
    
    if not filtered:
        return MonthlyResponse(
            total=0.0,
            entries=0,
            range_label="",
            monthly=[]
        )
    
    by_month: dict[str, float] = defaultdict(float)
    for e in filtered:
        by_month[e["date"][:7]] += e["amount"]
    
    grand = sum(by_month.values())
    dates = sorted(e["date"] for e in filtered)
    range_label = dates[0] if dates[0] == dates[-1] else f"{dates[0]} → {dates[-1]}"
    
    monthly = [
        MonthlyTotals(
            month=month,
            amount=amt,
            percentage=round(amt / grand * 100, 1)
        )
        for month, amt in sorted(by_month.items())
    ]
    
    return MonthlyResponse(
        total=round(grand, 2),
        entries=len(filtered),
        range_label=range_label,
        monthly=monthly
    )


@app.get("/api/categories")
def get_categories():
    """Get list of valid categories."""
    return CATEGORIES


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
