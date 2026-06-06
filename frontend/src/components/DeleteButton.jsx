import { Trash2 } from 'lucide-react';
import { deleteExpense } from '../api';

export default function DeleteButton({ id, onDelete }) {
  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this expense?')) return;
    
    try {
      await deleteExpense(id);
      onDelete();
    } catch (err) {
      alert('Failed to delete expense: ' + (err.message || 'Unknown error'));
    }
  };

  return (
    <button
      onClick={handleDelete}
      className="text-red-400 hover:text-red-300 transition-colors"
      title="Delete"
    >
      <Trash2 size={18} />
    </button>
  );
}
