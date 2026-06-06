"""
CLI Module
Command-line interface for expense tracker
"""
import sys
from datetime import datetime
from typing import Optional
from expense_tracker import ExpenseTracker
from storage import Storage


class ExpenseCLI:
    """Command-line interface for expense tracking"""
    
    def __init__(self, storage_path: str = "expenses.json"):
        self.tracker = ExpenseTracker()
        self.storage = Storage(storage_path)
        self._load_data()
    
    def _load_data(self):
        """Load expenses from storage"""
        try:
            expenses = self.storage.load_expenses()
            self.tracker.set_expenses(expenses)
        except Exception as e:
            print(f"Warning: Could not load expenses: {e}")
            print("Starting with empty expense list.")
    
    def _save_data(self):
        """Save expenses to storage"""
        try:
            self.storage.save_expenses(self.tracker.get_all_expenses())
        except Exception as e:
            print(f"Error: Could not save expenses: {e}")
            sys.exit(1)
    
    def _validate_amount(self, amount_str: str) -> float:
        """Validate and convert amount string to float"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            return amount
        except ValueError:
            raise ValueError("Invalid amount. Please enter a positive number.")
    
    def _validate_date(self, date_str: str) -> str:
        """Validate date format (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD (e.g., 2024-01-15)")
    
    def _format_currency(self, amount: float) -> str:
        """Format amount as currency"""
        return f"${amount:.2f}"
    
    def _print_expense(self, expense, index: Optional[int] = None):
        """Print a single expense"""
        prefix = f"{index}. " if index is not None else ""
        note = f" - {expense.note}" if expense.note else ""
        print(f"{prefix}{expense.date} | {expense.category} | {self._format_currency(expense.amount)}{note}")
        print(f"   ID: {expense.id}")
    
    def add_expense(self, amount: str, category: str, date: str, note: Optional[str] = None):
        """Add a new expense"""
        try:
            validated_amount = self._validate_amount(amount)
            validated_date = self._validate_date(date)
            
            if not category.strip():
                raise ValueError("Category cannot be empty")
            
            expense = self.tracker.add_expense(
                amount=validated_amount,
                category=category.strip(),
                date=validated_date,
                note=note.strip() if note else None
            )
            
            self._save_data()
            print("✓ Expense added successfully!")
            self._print_expense(expense)
        
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def list_expenses(self, category: Optional[str] = None, date: Optional[str] = None, 
                      start_date: Optional[str] = None, end_date: Optional[str] = None):
        """List expenses with optional filtering"""
        try:
            expenses = self.tracker.get_all_expenses()
            
            # Apply filters
            if category:
                expenses = self.tracker.filter_by_category(category)
            elif date:
                validated_date = self._validate_date(date)
                expenses = self.tracker.filter_by_date(validated_date)
            elif start_date and end_date:
                validated_start = self._validate_date(start_date)
                validated_end = self._validate_date(end_date)
                expenses = self.tracker.filter_by_date_range(validated_start, validated_end)
            
            if not expenses:
                print("No expenses found.")
                return
            
            print(f"\n{'='*70}")
            print(f"EXPENSES ({len(expenses)} entries)")
            print(f"{'='*70}")
            
            for i, expense in enumerate(expenses, 1):
                self._print_expense(expense, i)
                print()
            
            total = sum(e.amount for e in expenses)
            print(f"{'='*70}")
            print(f"Total: {self._format_currency(total)}")
            print(f"{'='*70}\n")
        
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def delete_expense(self, expense_id: str):
        """Delete an expense by ID"""
        try:
            if self.tracker.delete_expense(expense_id):
                self._save_data()
                print("✓ Expense deleted successfully!")
            else:
                print(f"Error: Expense with ID '{expense_id}' not found.")
                print("Use 'list' command to see all expense IDs.")
                sys.exit(1)
        
        except Exception as e:
            print(f"Error: Could not delete expense: {e}")
            sys.exit(1)
    
    def show_totals(self, category: Optional[str] = None):
        """Show total expenses and category breakdown"""
        try:
            expenses = self.tracker.get_all_expenses()
            
            if category:
                expenses = self.tracker.filter_by_category(category)
            
            if not expenses:
                print("No expenses found.")
                return
            
            total = sum(e.amount for e in expenses)
            
            print(f"\n{'='*70}")
            print("EXPENSE SUMMARY")
            print(f"{'='*70}")
            print(f"Total Expenses: {self._format_currency(total)}")
            print(f"Number of Entries: {len(expenses)}")
            print(f"{'='*70}\n")
            
            if not category:
                breakdown = self.tracker.get_category_breakdown()
                if breakdown:
                    print("CATEGORY BREAKDOWN:")
                    print(f"{'-'*70}")
                    for item in breakdown:
                        print(f"{item['category']:<20} {self._format_currency(item['amount']):>15} ({item['percentage']:>5.1f}%)")
                    print(f"{'-'*70}\n")
        
        except Exception as e:
            print(f"Error: Could not calculate totals: {e}")
            sys.exit(1)
    
    def show_categories(self):
        """Show all unique categories"""
        expenses = self.tracker.get_all_expenses()
        categories = sorted(set(e.category for e in expenses))
        
        if not categories:
            print("No categories found. Add some expenses first.")
            return
        
        print("\nCATEGORIES:")
        for cat in categories:
            print(f"  - {cat}")
        print()


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Expense Tracker CLI")
        print("\nUsage:")
        print("  python cli.py add <amount> <category> <date> [note]")
        print("  python cli.py list [--category <name>] [--date <YYYY-MM-DD>]")
        print("  python cli.py list [--from <YYYY-MM-DD>] [--to <YYYY-MM-DD>]")
        print("  python cli.py delete <expense_id>")
        print("  python cli.py totals [--category <name>]")
        print("  python cli.py categories")
        print("\nExamples:")
        print("  python cli.py add 25.50 groceries 2024-01-15 \"Weekly groceries\"")
        print("  python cli.py list --category groceries")
        print("  python cli.py list --date 2024-01-15")
        print("  python cli.py list --from 2024-01-01 --to 2024-01-31")
        print("  python cli.py delete abc123-def456-ghi789")
        print("  python cli.py totals")
        print("  python cli.py categories")
        sys.exit(1)
    
    cli = ExpenseCLI()
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) < 5:
            print("Error: add command requires amount, category, and date")
            print("Usage: python cli.py add <amount> <category> <date> [note]")
            sys.exit(1)
        
        amount = sys.argv[2]
        category = sys.argv[3]
        date = sys.argv[4]
        note = sys.argv[5] if len(sys.argv) > 5 else None
        
        cli.add_expense(amount, category, date, note)
    
    elif command == "list":
        category = None
        date = None
        start_date = None
        end_date = None
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--category" and i + 1 < len(sys.argv):
                category = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--date" and i + 1 < len(sys.argv):
                date = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--from" and i + 1 < len(sys.argv):
                start_date = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--to" and i + 1 < len(sys.argv):
                end_date = sys.argv[i + 1]
                i += 2
            else:
                print(f"Error: Unknown option '{sys.argv[i]}'")
                sys.exit(1)
        
        cli.list_expenses(category, date, start_date, end_date)
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: delete command requires expense ID")
            print("Usage: python cli.py delete <expense_id>")
            sys.exit(1)
        
        expense_id = sys.argv[2]
        cli.delete_expense(expense_id)
    
    elif command == "totals":
        category = None
        if len(sys.argv) > 2 and sys.argv[2] == "--category" and len(sys.argv) > 3:
            category = sys.argv[3]
        
        cli.show_totals(category)
    
    elif command == "categories":
        cli.show_categories()
    
    else:
        print(f"Error: Unknown command '{command}'")
        print("Run 'python cli.py' for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
