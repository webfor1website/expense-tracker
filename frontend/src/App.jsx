import { useState, useEffect } from 'react';
import { RotateCcw } from 'lucide-react';
import { getExpenses, getBreakdown, getMonthly, undoLast } from './api';
import AddExpenseForm from './components/AddExpenseForm';
import ExpenseTable from './components/ExpenseTable';
import Breakdown from './components/Breakdown';
import MonthlyChart from './components/MonthlyChart';

export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [breakdown, setBreakdown] = useState(null);
  const [monthly, setMonthly] = useState(null);
  const [filters, setFilters] = useState({
    category: '',
    from_date: '',
    to_date: '',
    last: ''
  });

  const fetchData = async () => {
    try {
      // Remove empty filter values
      const cleanFilters = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== '')
      );
      
      const filtered = await getExpenses(cleanFilters);
      setExpenses(Array.isArray(filtered) ? filtered : []);
      
      // Only send date filters if they have values
      const dateFilters = {};
      if (filters.from_date) dateFilters.from_date = filters.from_date;
      if (filters.to_date) dateFilters.to_date = filters.to_date;
      
      const bd = await getBreakdown(dateFilters);
      setBreakdown(bd);
      
      const mo = await getMonthly(dateFilters);
      setMonthly(mo);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setExpenses([]);
      setBreakdown(null);
      setMonthly(null);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  const handleAdd = () => {
    fetchData();
  };

  const handleDelete = () => {
    fetchData();
  };

  const handleUndo = async () => {
    try {
      await undoLast();
      fetchData();
    } catch (err) {
      alert('Failed to undo: ' + (err.message || 'Unknown error'));
    }
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const clearFilters = () => {
    setFilters({ category: '', from_date: '', to_date: '', last: '' });
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            💰 Expense Tracker
            <span className="text-sm font-normal text-gray-500">v3.1</span>
          </h1>
          <button
            onClick={handleUndo}
            className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded transition-colors"
          >
            <RotateCcw size={18} />
            Undo Last
          </button>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-1">
            <AddExpenseForm onAdd={handleAdd} />
          </div>
          
          <div className="lg:col-span-2">
            <div className="bg-gray-900 rounded-lg p-6 border border-gray-800 mb-6">
              <h2 className="text-xl font-bold text-white mb-4">Filters</h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-gray-400 text-sm mb-1">Category</label>
                  <input
                    type="text"
                    name="category"
                    value={filters.category}
                    onChange={handleFilterChange}
                    className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
                    placeholder="e.g. food"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-sm mb-1">From</label>
                  <input
                    type="date"
                    name="from_date"
                    value={filters.from_date}
                    onChange={handleFilterChange}
                    className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-sm mb-1">To</label>
                  <input
                    type="date"
                    name="to_date"
                    value={filters.to_date}
                    onChange={handleFilterChange}
                    className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-sm mb-1">Last N</label>
                  <input
                    type="number"
                    name="last"
                    value={filters.last}
                    onChange={handleFilterChange}
                    className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white focus:outline-none focus:border-cyan-400"
                    placeholder="e.g. 10"
                  />
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <button
                  onClick={fetchData}
                  className="bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-2 px-4 rounded transition-colors"
                >
                  Apply
                </button>
                <button
                  onClick={clearFilters}
                  className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition-colors"
                >
                  Clear
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <ExpenseTable expenses={expenses} onDelete={handleDelete} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Breakdown data={breakdown} />
          <MonthlyChart data={monthly} />
        </div>
      </div>
    </div>
  );
}
