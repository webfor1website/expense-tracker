import { useState, useEffect } from 'react';
import { PlusCircle } from 'lucide-react';
import { addExpense, getCategories } from '../api';

export default function AddExpenseForm({ onAdd }) {
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    amount: '',
    category: '',
    date: new Date().toISOString().split('T')[0],
    note: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    getCategories().then(setCategories);
  }, []);

  const validate = () => {
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      setError('Amount must be a positive number');
      return false;
    }
    if (!formData.category) {
      setError('Category is required');
      return false;
    }
    if (!formData.date) {
      setError('Date is required');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!validate()) return;

    try {
      await addExpense({
        amount: parseFloat(formData.amount),
        category: formData.category,
        date: formData.date,
        note: formData.note
      });
      setSuccess('Expense added successfully!');
      setFormData({
        amount: '',
        category: '',
        date: new Date().toISOString().split('T')[0],
        note: ''
      });
      onAdd();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to add expense');
    }
  };

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <PlusCircle className="text-cyan-400" />
        Add Expense
      </h2>
      
      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-900/50 border border-green-700 text-green-200 px-4 py-2 rounded mb-4">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-gray-400 text-sm mb-1">Amount</label>
            <input
              type="number"
              step="0.01"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
              placeholder="0.00"
            />
          </div>
          
          <div>
            <label className="block text-gray-400 text-sm mb-1">Category</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
            >
              <option value="">Select category</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-gray-400 text-sm mb-1">Date</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-gray-400 text-sm mb-1">Note (optional)</label>
          <input
            type="text"
            value={formData.note}
            onChange={(e) => setFormData({ ...formData, note: e.target.value })}
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
            placeholder="Add a note..."
          />
        </div>
        
        <button
          type="submit"
          className="w-full bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-2 px-4 rounded transition-colors"
        >
          Add Expense
        </button>
      </form>
    </div>
  );
}
