"""
Expense Tracker Core Module
Handles expense data model and business logic
"""
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid


@dataclass
class Expense:
    """Represents a single expense entry"""
    id: str
    amount: float
    category: str
    date: str
    note: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert expense to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Expense':
        """Create expense from dictionary"""
        return cls(**data)

    @classmethod
    def create(cls, amount: float, category: str, date: str, note: Optional[str] = None) -> 'Expense':
        """Create a new expense with generated ID"""
        return cls(
            id=str(uuid.uuid4()),
            amount=amount,
            category=category,
            date=date,
            note=note
        )


class ExpenseTracker:
    """Main expense tracker class"""
    
    def __init__(self):
        self.expenses: List[Expense] = []
    
    def add_expense(self, amount: float, category: str, date: str, note: Optional[str] = None) -> Expense:
        """Add a new expense"""
        expense = Expense.create(amount, category, date, note)
        self.expenses.append(expense)
        return expense
    
    def get_all_expenses(self) -> List[Expense]:
        """Get all expenses"""
        return self.expenses
    
    def filter_by_category(self, category: str) -> List[Expense]:
        """Filter expenses by category"""
        return [e for e in self.expenses if e.category.lower() == category.lower()]
    
    def filter_by_date(self, date: str) -> List[Expense]:
        """Filter expenses by date"""
        return [e for e in self.expenses if e.date == date]
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> List[Expense]:
        """Filter expenses by date range"""
        return [e for e in self.expenses if start_date <= e.date <= end_date]
    
    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense by ID"""
        for i, expense in enumerate(self.expenses):
            if expense.id == expense_id:
                self.expenses.pop(i)
                return True
        return False
    
    def get_total(self) -> float:
        """Get total of all expenses"""
        return sum(e.amount for e in self.expenses)
    
    def get_category_totals(self) -> Dict[str, float]:
        """Get total expenses by category"""
        totals = {}
        for expense in self.expenses:
            category = expense.category
            totals[category] = totals.get(category, 0) + expense.amount
        return totals
    
    def get_category_breakdown(self) -> List[Dict[str, any]]:
        """Get detailed category breakdown with percentages"""
        totals = self.get_category_totals()
        total = self.get_total()
        breakdown = []
        for category, amount in totals.items():
            percentage = (amount / total * 100) if total > 0 else 0
            breakdown.append({
                'category': category,
                'amount': amount,
                'percentage': round(percentage, 2)
            })
        # Sort by amount descending
        breakdown.sort(key=lambda x: x['amount'], reverse=True)
        return breakdown
    
    def set_expenses(self, expenses: List[Expense]):
        """Set expenses from storage"""
        self.expenses = expenses
