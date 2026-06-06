import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Calendar } from 'lucide-react';

export default function MonthlyChart({ data }) {
  if (!data || !data.monthly || data.monthly.length === 0) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Calendar className="text-cyan-400" />
          Monthly Totals
        </h2>
        <p className="text-gray-500 text-center py-8">No data available</p>
      </div>
    );
  }

  const chartData = data.monthly.map(item => ({
    month: item.month,
    amount: item.amount,
    percentage: item.percentage
  }));

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <Calendar className="text-cyan-400" />
        Monthly Totals
      </h2>
      
      <div className="h-48 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <XAxis 
              dataKey="month" 
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
              formatter={(value, name, props) => [
                `$${value.toFixed(2)} (${props.payload.percentage}%)`,
                name
              ]}
            />
            <Bar dataKey="amount" fill="#a855f7" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="space-y-2">
        {data.monthly.map((item) => (
          <div key={item.month} className="flex items-center justify-between">
            <span className="text-white">{item.month}</span>
            <div className="text-right">
              <span className="text-purple-400 font-semibold">${item.amount.toFixed(2)}</span>
              <span className="text-gray-500 text-sm ml-2">{item.percentage}%</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-800 flex justify-between items-center">
        <span className="text-gray-400">Total</span>
        <span className="text-purple-400 font-bold text-lg">${data.total.toFixed(2)}</span>
      </div>
    </div>
  );
}
