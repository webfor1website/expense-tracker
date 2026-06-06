"""
Storage Module
Handles JSON persistence with validation
"""
import json
import os
from typing import List, Dict, Optional
from expense_tracker import Expense


class Storage:
    """Handles JSON file storage for expenses"""
    
    def __init__(self, file_path: str = "expenses.json"):
        self.file_path = file_path
    
    def _validate_expense_data(self, data: Dict) -> bool:
        """Validate expense data structure"""
        required_fields = ['id', 'amount', 'category', 'date']
        for field in required_fields:
            if field not in data:
                return False
        # Validate types
        if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
            return False
        if not isinstance(data['category'], str) or not data['category'].strip():
            return False
        if not isinstance(data['date'], str) or not data['date'].strip():
            return False
        return True
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD)"""
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def load_expenses(self) -> List[Expense]:
        """Load expenses from JSON file"""
        if not os.path.exists(self.file_path):
            return []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("Invalid data format: expected list")
            
            expenses = []
            for item in data:
                if not self._validate_expense_data(item):
                    print(f"Warning: Skipping invalid expense data: {item}")
                    continue
                
                if not self._validate_date_format(item['date']):
                    print(f"Warning: Skipping expense with invalid date format: {item['date']}")
                    continue
                
                expense = Expense.from_dict(item)
                expenses.append(expense)
            
            return expenses
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading expenses: {e}")
    
    def save_expenses(self, expenses: List[Expense]) -> None:
        """Save expenses to JSON file"""
        try:
            data = [expense.to_dict() for expense in expenses]
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            raise ValueError(f"Error saving expenses: {e}")
    
    def backup_expenses(self) -> str:
        """Create a backup of the current expenses file"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError("No expenses file to backup")
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.file_path}.backup_{timestamp}"
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            return backup_path
        except Exception as e:
            raise ValueError(f"Error creating backup: {e}")
