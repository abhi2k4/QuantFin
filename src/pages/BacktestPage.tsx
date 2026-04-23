import { useState } from 'react';
import { motion } from 'framer-motion';
import { IconTrendingUp, IconTrendingDown, IconActivity, IconCurrencyDollar, IconChartBar, IconCalendar, IconSettings, IconPlayerPlay, IconLoader, IconAlertCircle, IconCircleCheck } from '@tabler/icons-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { 
  runBacktest, 
  type BacktestRequest, 
  type BacktestResponse,
  getErrorMessage
} from '@/services/api';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

export default function BacktestPage() {
  // Backtest configuration
  const [strategy, setStrategy] = useState<string>('LINEAR');
  const [startDate, setStartDate] = useState<string>('2023-01-01');
  const [endDate, setEndDate] = useState<string>('2024-12-31');
  const [capital, setCapital] = useState<number>(100000);
  const [topN, setTopN] = useState<number>(10);
  const [rebalanceFreq, setRebalanceFreq] = useState<string>('monthly');
  
  // Results
  const [results, setResults] = useState<BacktestResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRunBacktest = async () => {
    if (!startDate || !endDate) {
      toast.error('Please select start and end dates');
      return;
    }

    if (new Date(startDate) >= new Date(endDate)) {
      toast.error('Start date must be before end date');
      return;
    }

    setLoading(true);
    try {
      const request: BacktestRequest = {
        strategy,
        start_date: startDate,
        end_date: endDate,
        capital,
        top_n: topN,
        rebalance_frequency: rebalanceFreq
      };

      const response = await runBacktest(request);
      setResults(response);
      toast.success('Backtest completed successfully!');
    } catch (error) {
      console.error('Backtest error:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const chartData = results ? results.dates.map((date, idx) => ({
    date: new Date(date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
    strategy: results.portfolio_values[idx],
    benchmark: results.benchmark_values[idx]
  })) : [];

  return (
    <div className="min-h-screen bg-bg-[#0d0d0d] text-white">
      {/* Header Section */}
      <div className="border-b border-[rgba(255,255,255,0.06)] bg-[rgba(13,13,13,0.9)] backdrop-blur-xl">
        <div className="max-w-[1600px] mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Strategy Backtesting</h1>
              <p className="text-sm text-gray-400 mt-1">Test ML strategies with walk-forward simulation</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-6 py-8 space-y-8">
        {/* Configuration Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="bg-[#141414] border-[rgba(255,255,255,0.07)] p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-[rgba(200,255,0,0.1)] border border-[rgba(200,255,0,0.2)] rounded-lg">
                <IconSettings className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-xl font-semibold">Backtest Configuration</h2>
            </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Strategy Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                ML Strategy
              </label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="w-full bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-[#c8ff00]/30 focus:border-transparent appearance-none cursor-pointer hover:bg-white/10 transition-colors"
                style={{ colorScheme: 'dark' }}
              >
                <option value="LINEAR" className="bg-gray-800 text-white">Linear Regression</option>
                <option value="SVM" className="bg-gray-800 text-white">Support Vector Machine</option>
                <option value="LSTM" className="bg-gray-800 text-white">LSTM (Deep Learning)</option>
                <option value="ARIMA" className="bg-gray-800 text-white">ARIMA (Time Series)</option>
              </select>
            </div>

            {/* Start Date */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-[#c8ff00]/30 focus:border-transparent"
              />
            </div>

            {/* End Date */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-[#c8ff00]/30 focus:border-transparent"
              />
            </div>

            {/* Initial Capital */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Initial Capital (₹)
              </label>
              <input
                type="number"
                value={capital}
                onChange={(e) => setCapital(Number(e.target.value))}
                className="w-full bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-[#c8ff00]/30 focus:border-transparent"
                min={10000}
                step={10000}
              />
            </div>

            {/* Top N Stocks */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Top N Stocks
              </label>
              <input
                type="number"
                value={topN}
                onChange={(e) => setTopN(Number(e.target.value))}
                className="w-full bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-[#c8ff00]/30 focus:border-transparent"
                min={5}
                max={20}
              />
            </div>

            {/* Rebalance Frequency */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Rebalance Frequency
              </label>
              <select
                value={rebalanceFreq}
                onChange={(e) => setRebalanceFreq(e.target.value)}
                className="w-full bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-[#c8ff00]/30 focus:border-transparent appearance-none cursor-pointer hover:bg-white/10 transition-colors"
                style={{ colorScheme: 'dark' }}
              >
                <option value="monthly" className="bg-gray-800 text-white">Monthly</option>
                <option value="quarterly" className="bg-gray-800 text-white">Quarterly</option>
              </select>
            </div>
          </div>

          {/* Run Button */}
          <div className="mt-6">
            <Button
              onClick={handleRunBacktest}
              disabled={loading}
              className="rounded-xl bg-[#c8ff00] text-black hover:bg-[#d8ff33] border-0"
            >
              {loading ? (
                <>
                  <IconLoader className="w-4 h-4 mr-2 animate-spin" />
                  Running Backtest...
                </>
              ) : (
                <>
                  <IconPlayerPlay className="w-4 h-4 mr-2" />
                  Run Backtest
                </>
              )}
            </Button>
          </div>
        </Card>
      </motion.div>

        {/* Results */}
        {results && (
          <>
            {/* Performance Metrics */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
            >
              {/* Strategy CAGR */}
              <Card className="bg-[#141414] border-[rgba(255,255,255,0.07)] p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Strategy CAGR</p>
                    <p className="text-3xl font-bold text-blue-400">
                      {results.strategy_cagr.toFixed(2)}%
                    </p>
                  </div>
                  <div className="p-3 bg-blue-500/20 rounded-lg">
                    <IconTrendingUp className="w-6 h-6 text-[#c8ff00]" />
                  </div>
                </div>
              </Card>

              {/* Benchmark CAGR */}
              <Card className="bg-[#141414] border-[rgba(255,255,255,0.07)] p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Benchmark CAGR</p>
                    <p className="text-3xl font-bold text-[#a0a0a0]">
                      {results.benchmark_cagr.toFixed(2)}%
                    </p>
                  </div>
                  <div className="p-3 bg-purple-500/20 rounded-lg">
                    <IconChartBar className="w-6 h-6 text-[#a0a0a0]" />
                  </div>
                </div>
              </Card>

              {/* Sharpe Ratio */}
              <Card className="bg-[#141414] border-[rgba(255,255,255,0.07)] p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Sharpe Ratio</p>
                    <p className="text-3xl font-bold text-green-400">
                      {results.strategy_sharpe.toFixed(2)}
                    </p>
                  </div>
                  <div className="p-3 bg-green-500/20 rounded-lg">
                    <IconActivity className="w-6 h-6 text-green-400" />
                  </div>
                </div>
              </Card>

              {/* Max Drawdown */}
              <Card className="bg-[#141414] border-[rgba(255,255,255,0.07)] p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Max Drawdown</p>
                    <p className="text-3xl font-bold text-red-400">
                      {results.strategy_max_drawdown.toFixed(2)}%
                    </p>
                  </div>
                  <div className="p-3 bg-red-500/20 rounded-lg">
                    <IconTrendingDown className="w-6 h-6 text-red-400" />
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Portfolio Value Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card className="bg-[#141414] border-[rgba(255,255,255,0.07)] p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-[rgba(200,255,0,0.1)] border border-[rgba(200,255,0,0.2)] rounded-lg">
                    <IconChartBar className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold">Portfolio Value Over Time</h3>
                </div>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis 
                      dataKey="date" 
                      stroke="#9CA3AF"
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis 
                      stroke="#9CA3AF"
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1a1a1a', 
                        border: '1px solid rgba(255,255,255,0.08)',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number) => [`₹${value.toLocaleString()}`, '']}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="strategy" 
                      stroke="#3B82F6" 
                      strokeWidth={2}
                      name="Strategy"
                      dot={false}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="benchmark" 
                      stroke="#9ca3af" 
                      strokeWidth={2}
                      name="Benchmark (Equal-Weighted Nifty50)"
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </motion.div>

            {/* Detailed Metrics Comparison */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <Card className="bg-[#141414] border-[rgba(255,255,255,0.07)] p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-[rgba(200,255,0,0.1)] border border-[rgba(200,255,0,0.2)] rounded-lg">
                    <IconActivity className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold">Detailed Metrics Comparison</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Strategy Metrics */}
                  <div className="bg-[#1a1a1a] rounded-lg p-5 border border-[rgba(255,255,255,0.07)]">
                    <h4 className="text-lg font-medium text-[#c8ff00] mb-4 flex items-center gap-2">
                      <div className="w-2 h-2 bg-[#c8ff00] rounded-full"></div>
                      Strategy Performance
                    </h4>
                    <div className="space-y-3">
                      <MetricRow label="CAGR" value={`${results.strategy_cagr.toFixed(2)}%`} />
                      <MetricRow label="Sharpe Ratio" value={results.strategy_sharpe.toFixed(2)} />
                      <MetricRow label="Sortino Ratio" value={results.strategy_sortino.toFixed(2)} />
                      <MetricRow label="Max Drawdown" value={`${results.strategy_max_drawdown.toFixed(2)}%`} />
                      <MetricRow label="Volatility" value={`${results.strategy_volatility.toFixed(2)}%`} />
                      <MetricRow label="Calmar Ratio" value={results.strategy_calmar.toFixed(2)} />
                      <MetricRow label="Win Rate" value={`${results.strategy_win_rate.toFixed(2)}%`} />
                    </div>
                  </div>

                  {/* Benchmark Metrics */}
                  <div className="bg-[#1a1a1a] rounded-lg p-5 border border-[rgba(255,255,255,0.07)]">
                    <h4 className="text-lg font-medium text-[#a0a0a0] mb-4 flex items-center gap-2">
                      <div className="w-2 h-2 bg-[#a0a0a0] rounded-full"></div>
                      Benchmark Performance
                    </h4>
                    <div className="space-y-3">
                      <MetricRow label="CAGR" value={`${results.benchmark_cagr.toFixed(2)}%`} />
                      <MetricRow label="Sharpe Ratio" value={results.benchmark_sharpe.toFixed(2)} />
                      <MetricRow label="Sortino Ratio" value={results.benchmark_sortino.toFixed(2)} />
                      <MetricRow label="Max Drawdown" value={`${results.benchmark_max_drawdown.toFixed(2)}%`} />
                      <MetricRow label="Volatility" value={`${results.benchmark_volatility.toFixed(2)}%`} />
                      <MetricRow label="Calmar Ratio" value={results.benchmark_calmar.toFixed(2)} />
                      <MetricRow label="Win Rate" value={`${results.benchmark_win_rate.toFixed(2)}%`} />
                    </div>
                  </div>
                </div>

                {/* Summary Stats */}
                <div className="mt-6 pt-6 border-t border-white/10">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
                      <p className="text-gray-400 text-sm mb-1">Initial Capital</p>
                      <p className="text-xl font-bold text-white">₹{results.initial_capital.toLocaleString()}</p>
                    </div>
                    <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
                      <p className="text-gray-400 text-sm mb-1">Final Value</p>
                      <p className="text-xl font-bold text-white">₹{results.final_value.toLocaleString()}</p>
                    </div>
                    <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
                      <p className="text-gray-400 text-sm mb-1">Total Return</p>
                      <p className={`text-xl font-bold ${
                        results.final_value >= results.initial_capital ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {(((results.final_value - results.initial_capital) / results.initial_capital) * 100).toFixed(2)}%
                      </p>
                    </div>
                    <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
                      <p className="text-gray-400 text-sm mb-1">Rebalances</p>
                      <p className="text-xl font-bold text-white">{results.num_rebalances}</p>
                    </div>
                  </div>
                </div>

                {/* Outperformance Badge */}
                <div className="mt-6">
                  {results.strategy_cagr > results.benchmark_cagr ? (
                    <div className="flex items-center gap-3 text-[#c8ff00] bg-[rgba(200,255,0,0.05)] border border-[rgba(200,255,0,0.2)] rounded-lg px-5 py-4">
                      <IconCircleCheck className="w-6 h-6" />
                      <div>
                        <p className="font-semibold text-lg">Strategy Outperformed!</p>
                        <p className="text-sm text-gray-400">
                          Beat benchmark by {(results.strategy_cagr - results.benchmark_cagr).toFixed(2)}% CAGR
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-3 text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-5 py-4">
                      <IconAlertCircle className="w-6 h-6" />
                      <div>
                        <p className="font-semibold text-lg">Strategy Underperformed</p>
                        <p className="text-sm text-gray-400">
                          Trailed benchmark by {(results.benchmark_cagr - results.strategy_cagr).toFixed(2)}% CAGR
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
}

// Helper component for metric rows
function MetricRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
      <span className="text-gray-400 text-sm">{label}</span>
      <span className="text-white font-semibold">{value}</span>
    </div>
  );
}
