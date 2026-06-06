import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { BarChart2 } from 'lucide-react';

export default function Breakdown({ data }) {
  if (!data || !data.breakdown || data.breakdown.length === 0) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <BarChart2 className="text-cyan-400" />
          Category Breakdown
        </h2>
        <p className="text-gray-500 text-center py-8">No data available</p>
      </div>
    );
  }

  const chartData = data.breakdown.map(item => ({
    category: item.category,
    amount: item.amount
  }));

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <BarChart2 className="text-cyan-400" />
        Category Breakdown
      </h2>
      
      <div className="h-48 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <XAxis 
              dataKey="category" 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af' }}
            />
            <YAxis 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              itemStyle={{ color: '#fff' }}
            />
            <Bar dataKey="amount" fill="#22d3ee" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="space-y-2">
        {data.breakdown.map((item) => (
          <div key={item.category} className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <span className="text-white capitalize w-24">{item.category}</span>
              <div className="flex-1 bg-gray-800 rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-cyan-400 h-full"
                  style={{ width: `${item.percentage}%` }}
                />
              </div>
            </div>
            <div className="text-right ml-4">
              <span className="text-cyan-400 font-semibold">${item.amount.toFixed(2)}</span>
              <span className="text-gray-500 text-sm ml-2">{item.percentage}%</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-800 flex justify-between items-center">
        <span className="text-gray-400">Total</span>
        <span className="text-cyan-400 font-bold text-lg">${data.total.toFixed(2)}</span>
      </div>
    </div>
  );
}
