import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PlayCircle, BarChart3, TrendingUp, TrendingDown, Activity, Target, Loader2, RefreshCw } from 'lucide-react';
import { runBacktest, getErrorMessage, type BacktestResponse, type BacktestRequest } from '@/services/api';
import { toast } from 'sonner';

export default function BacktestResults() {
  const [backtestData, setBacktestData] = useState<BacktestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<'model_weighted' | 'mean_variance' | 'risk_parity'>('model_weighted');

  // Default stocks for backtest
  const defaultSymbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK'];

  useEffect(() => {
    loadBacktest();
  }, []);

  const loadBacktest = async (strategy: string = 'model_weighted') => {
    setLoading(true);
    try {
      const request: BacktestRequest = {
        symbols: defaultSymbols,
        start_date: '2024-01-01',
        end_date: '2025-09-30',
        strategy: strategy,
        rebalance_freq: 21,
        initial_capital: 100000,
        transaction_cost: 0.001
      };

      const data = await runBacktest(request);
      setBacktestData(data);
      toast.success('Backtest completed successfully!');
    } catch (error) {
      console.error('Error running backtest:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleRunBacktest = (strategy: string) => {
    setSelectedStrategy(strategy as any);
    loadBacktest(strategy);
  };

  // Format data for charts
  const chartData = backtestData?.daily_results.map((result, idx) => ({
    date: new Date(result.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    value: result.portfolio_value,
    return: (backtestData.cumulative_returns[idx] * 100).toFixed(2),
    drawdown: (backtestData.drawdowns[idx] * 100).toFixed(2)
  })) || [];

  const metrics = backtestData?.metrics;

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 text-white">
        {/* Top Bar */}
        <div className="sticky top-0 z-50 backdrop-blur-xl bg-zinc-950/80 border-b border-white/5">
          <div className="max-w-[1600px] mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-3">
                  <BarChart3 className="w-6 h-6 text-cyan-400" />
                  Backtest Results
                </h1>
                <p className="text-sm text-gray-400 mt-1">Historical strategy performance analysis</p>
              </div>
              <div className="flex gap-3">
                <Button
                  onClick={() => loadBacktest(selectedStrategy)}
                  disabled={loading}
                  className="rounded-xl bg-white/5 hover:bg-white/10 border border-white/10"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-[1600px] mx-auto px-6 py-6 space-y-6">
          {/* Strategy Selection */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3"
          >
            {[
              { value: 'model_weighted', label: 'Model Weighted', desc: 'ML Predictions' },
              { value: 'mean_variance', label: 'Mean Variance', desc: 'Markowitz Optimization' },
              { value: 'risk_parity', label: 'Risk Parity', desc: 'Equal Risk' }
            ].map((strategy) => (
              <Button
                key={strategy.value}
                onClick={() => handleRunBacktest(strategy.value)}
                disabled={loading}
                className={`flex-1 h-auto py-4 rounded-xl ${
                  selectedStrategy === strategy.value
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0'
                    : 'bg-white/5 hover:bg-white/10 border border-white/10'
                }`}
              >
                <div className="flex flex-col items-center gap-1">
                  <span className="font-semibold">{strategy.label}</span>
                  <span className="text-xs opacity-70">{strategy.desc}</span>
                </div>
              </Button>
            ))}
          </motion.div>

          {loading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-20"
            >
              <Loader2 className="w-12 h-12 text-blue-400 animate-spin mb-4" />
              <p className="text-gray-400">Running backtest simulation...</p>
              <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
            </motion.div>
          ) : backtestData ? (
            <>
              {/* Metrics Cards */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
              >
                <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-gray-400 mb-1">Total Return</p>
                      <p className="text-3xl font-bold text-green-400">
                        {(metrics!.total_return * 100).toFixed(2)}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Final: ₹{metrics!.final_value.toLocaleString()}
                      </p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-green-400 opacity-50" />
                  </div>
                </Card>

                <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-gray-400 mb-1">Sharpe Ratio</p>
                      <p className="text-3xl font-bold text-blue-400">
                        {metrics!.sharpe_ratio.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Risk-adjusted return
                      </p>
                    </div>
                    <Target className="w-8 h-8 text-blue-400 opacity-50" />
                  </div>
                </Card>

                <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-gray-400 mb-1">Max Drawdown</p>
                      <p className="text-3xl font-bold text-red-400">
                        {(metrics!.max_drawdown * 100).toFixed(2)}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Peak to trough
                      </p>
                    </div>
                    <TrendingDown className="w-8 h-8 text-red-400 opacity-50" />
                  </div>
                </Card>

                <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-gray-400 mb-1">Win Rate</p>
                      <p className="text-3xl font-bold text-purple-400">
                        {(metrics!.win_rate * 100).toFixed(1)}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {metrics!.num_trades} trades
                      </p>
                    </div>
                    <Activity className="w-8 h-8 text-purple-400 opacity-50" />
                  </div>
                </Card>
              </motion.div>

              {/* Portfolio Value Chart */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-green-400" />
                    Portfolio Value Over Time
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="valueGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                      <XAxis
                        dataKey="date"
                        stroke="#9ca3af"
                        tick={{ fontSize: 12 }}
                        tickLine={false}
                      />
                      <YAxis
                        stroke="#9ca3af"
                        tick={{ fontSize: 12 }}
                        tickLine={false}
                        tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(0, 0, 0, 0.8)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '8px',
                          color: '#fff'
                        }}
                        formatter={(value: any) => [`₹${Number(value).toLocaleString()}`, 'Portfolio Value']}
                      />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        fill="url(#valueGradient)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Card>
              </motion.div>

              {/* Cumulative Returns & Drawdown */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="grid md:grid-cols-2 gap-6"
              >
                <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-green-400" />
                    Cumulative Returns
                  </h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                      <XAxis dataKey="date" stroke="#9ca3af" tick={{ fontSize: 11 }} />
                      <YAxis stroke="#9ca3af" tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(0, 0, 0, 0.8)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '8px'
                        }}
                      />
                      <Line type="monotone" dataKey="return" stroke="#10b981" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>

                <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <TrendingDown className="w-5 h-5 text-red-400" />
                    Drawdown
                  </h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                      <XAxis dataKey="date" stroke="#9ca3af" tick={{ fontSize: 11 }} />
                      <YAxis stroke="#9ca3af" tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(0, 0, 0, 0.8)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '8px'
                        }}
                      />
                      <Line type="monotone" dataKey="drawdown" stroke="#ef4444" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </motion.div>

              {/* Configuration & Warnings */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                  <h3 className="text-lg font-semibold mb-4">Backtest Configuration</h3>
                  <div className="grid md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-400">Symbols:</p>
                      <p className="text-white font-mono">{backtestData.configuration.symbols.join(', ')}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Strategy:</p>
                      <p className="text-white capitalize">{backtestData.configuration.strategy.replace('_', ' ')}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Period:</p>
                      <p className="text-white">{backtestData.configuration.start_date} to {backtestData.configuration.end_date}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Initial Capital:</p>
                      <p className="text-white">₹{backtestData.configuration.initial_capital.toLocaleString()}</p>
                    </div>
                  </div>
                  {backtestData.warnings.length > 0 && (
                    <div className="mt-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                      <p className="text-sm text-yellow-400 font-semibold mb-2">Warnings:</p>
                      {backtestData.warnings.map((warning, idx) => (
                        <p key={idx} className="text-xs text-yellow-300">• {warning}</p>
                      ))}
                    </div>
                  )}
                </Card>
              </motion.div>
            </>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20"
            >
              <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 mb-4">No backtest results available</p>
              <Button
                onClick={() => loadBacktest()}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                <PlayCircle className="w-4 h-4 mr-2" />
                Run Backtest
              </Button>
            </motion.div>
          )}
        </div>
      </div>
    </>
  );
}
