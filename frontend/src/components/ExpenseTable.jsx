import { List } from 'lucide-react';
import DeleteButton from './DeleteButton';

export default function ExpenseTable({ expenses, onDelete }) {
  if (!expenses || expenses.length === 0) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <List className="text-cyan-400" />
          Expenses
        </h2>
        <p className="text-gray-500 text-center py-8">No expenses found</p>
      </div>
    );
  }

  const total = expenses.reduce((sum, e) => sum + e.amount, 0);

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <List className="text-cyan-400" />
        Expenses ({expenses.length})
      </h2>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-400 text-sm border-b border-gray-800">
              <th className="pb-3 pr-4">ID</th>
              <th className="pb-3 pr-4">Date</th>
              <th className="pb-3 pr-4">Category</th>
              <th className="pb-3 pr-4">Amount</th>
              <th className="pb-3 pr-4">Note</th>
              <th className="pb-3"></th>
            </tr>
          </thead>
          <tbody>
            {expenses.map((expense) => (
              <tr key={expense.id} className="border-b border-gray-800 text-white">
                <td className="py-3 pr-4 text-gray-400">#{expense.id}</td>
                <td className="py-3 pr-4">{expense.date}</td>
                <td className="py-3 pr-4">
                  <span className="bg-gray-800 px-2 py-1 rounded text-sm capitalize">
                    {expense.category}
                  </span>
                </td>
                <td className="py-3 pr-4 text-cyan-400 font-semibold">
                  ${expense.amount.toFixed(2)}
                </td>
                <td className="py-3 pr-4 text-gray-400 text-sm max-w-xs truncate">
                  {expense.note || '-'}
                </td>
                <td className="py-3">
                  <DeleteButton id={expense.id} onDelete={onDelete} />
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t-2 border-gray-700">
              <td colSpan="3" className="py-3 text-right font-bold text-white">
                Total:
              </td>
              <td className="py-3 text-cyan-400 font-bold text-lg">
                ${total.toFixed(2)}
              </td>
              <td colSpan="2"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
