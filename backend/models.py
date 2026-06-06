from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date

CATEGORIES = [
    "food", "transport", "housing", "utilities", "health",
    "entertainment", "shopping", "education", "travel", "other"
]


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: Optional[str] = None
    note: Optional[str] = ""

    @field_validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than zero")
        return round(v, 2)

    @field_validator("category")
    def category_valid(cls, v):
        if v.lower() not in CATEGORIES:
            raise ValueError(f"unknown category '{v}'. Valid: {', '.join(CATEGORIES)}")
        return v.lower()

    @field_validator("date", mode="before")
    def date_format(cls, v):
        if v is None:
            return date.today().isoformat()
        try:
            from datetime import datetime
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError(f"date must be YYYY-MM-DD, got '{v}'")


class Expense(ExpenseCreate):
    id: int


class UndoResponse(BaseModel):
    message: str
    action: Optional[str] = None


class CategoryTotals(BaseModel):
    category: str
    amount: float
    percentage: float


class BreakdownResponse(BaseModel):
    total: float
    entries: int
    range_label: str
    breakdown: list[CategoryTotals]


class MonthlyTotals(BaseModel):
    month: str
    amount: float
    percentage: float


class MonthlyResponse(BaseModel):
    total: float
    entries: int
    range_label: str
    monthly: list[MonthlyTotals]
