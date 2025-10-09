import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  DollarSign,
  Activity,
  RefreshCw,
  Loader2,
  ChevronDown,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  Sparkles,
  BrainCircuit,
  BarChart4
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  getPortfolioSummary,
  getPortfolioPerformance,
  rebalancePortfolio,
  getErrorMessage,
  type PortfolioSummary,
  type PortfolioPerformance,
  type Position,
  type RebalanceRequest
} from '@/services/api';
import { toast } from 'sonner';

type Timeframe = '1M' | '3M' | '6M' | '1Y';
type ModelStrategy = 'LSTM' | 'Linear' | 'Logistic' | 'SVM';

export default function Dashboard() {
  // State management
  const navigate = useNavigate();
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [performance, setPerformance] = useState<PortfolioPerformance | null>(null);
  const [timeframe, setTimeframe] = useState<Timeframe>('3M');
  const [selectedStrategy, setSelectedStrategy] = useState<ModelStrategy>('LSTM');
  const [capitalAllocation, setCapitalAllocation] = useState<string>('');
  
  // Loading states
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [loadingPerformance, setLoadingPerformance] = useState(true);
  const [rebalancing, setRebalancing] = useState(false);

  // Sorting state for positions table
  const [sortKey, setSortKey] = useState<keyof Position>('symbol');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // Load data on mount and when filters change
  useEffect(() => {
    loadPortfolioSummary();
  }, []);

  useEffect(() => {
    loadPortfolioPerformance();
  }, [timeframe]);

  const loadPortfolioSummary = async () => {
    setLoadingSummary(true);
    try {
      const data = await getPortfolioSummary();
      // Calculate allocations
      const totalValue = data.positions.reduce((sum, pos) => sum + (pos.quantity * pos.current_price), 0);
      data.positions = data.positions.map(pos => ({
        ...pos,
        allocation: ((pos.quantity * pos.current_price) / totalValue) * 100
      }));
      setSummary(data);
    } catch (error) {
      console.error('Error loading portfolio summary:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoadingSummary(false);
    }
  };

  const loadPortfolioPerformance = async () => {
    setLoadingPerformance(true);
    try {
      const data = await getPortfolioPerformance(timeframe);
      setPerformance(data);
    } catch (error) {
      console.error('Error loading portfolio performance:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoadingPerformance(false);
    }
  };

  const handleRebalance = async () => {
    const allocation = parseFloat(capitalAllocation);
    if (isNaN(allocation) || allocation <= 0) {
      toast.error('Please enter a valid capital allocation amount');
      return;
    }

    if (!summary || allocation > summary.cash_balance) {
      toast.error('Capital allocation exceeds available cash balance');
      return;
    }

    setRebalancing(true);
    try {
      const request: RebalanceRequest = {
        strategy: selectedStrategy,
        capital_allocation: allocation
      };
      const result = await rebalancePortfolio(request);
      
      // Result now contains the full portfolio summary plus allocations
      setSummary(result as any);  // Backend returns PortfolioSummary structure
      
      toast.success(`Portfolio rebalanced successfully using ${selectedStrategy} strategy! Expected return: ${result.expected_return}%`);
      setCapitalAllocation('');
      
      // Reload performance data
      loadPortfolioPerformance();
    } catch (error) {
      console.error('Error rebalancing portfolio:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setRebalancing(false);
    }
  };

  const handleSort = (key: keyof Position) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortOrder('asc');
    }
  };

  const sortedPositions = summary?.positions.sort((a, b) => {
    const aValue = a[sortKey] || 0;
    const bValue = b[sortKey] || 0;
    if (sortOrder === 'asc') {
      return aValue < bValue ? -1 : 1;
    } else {
      return aValue > bValue ? -1 : 1;
    }
  }) || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 text-white">
      {/* Top Bar */}
      <div className="sticky top-0 z-50 backdrop-blur-xl bg-zinc-950/80 border-b border-white/5">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Portfolio Dashboard</h1>
              <p className="text-sm text-gray-400 mt-1">Real-time portfolio management & insights</p>
            </div>
            <div className="flex gap-3">
              <Button
                onClick={() => navigate('/analytics')}
                className="rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0"
              >
                <BrainCircuit className="w-4 h-4 mr-2" />
                ML Analytics
              </Button>
              <Button
                onClick={() => navigate('/backtest')}
                className="rounded-xl bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white border-0"
              >
                <BarChart4 className="w-4 h-4 mr-2" />
                Backtesting
              </Button>
              <Button
                onClick={() => {
                  loadPortfolioSummary();
                  loadPortfolioPerformance();
                }}
                className="rounded-xl bg-white/5 hover:bg-white/10 border border-white/10"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-6 py-8 space-y-8">
        {/* Portfolio Summary Cards */}
        <PortfolioSummaryCards summary={summary} loading={loadingSummary} />

        {/* Main Grid - Performance Chart & Allocation */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Performance Chart - 2/3 width */}
          <div className="lg:col-span-2">
            <PerformanceChart
              data={performance}
              timeframe={timeframe}
              onTimeframeChange={setTimeframe}
              loading={loadingPerformance}
            />
          </div>

          {/* Allocation Pie Chart - 1/3 width */}
          <div className="lg:col-span-1">
            <AllocationChart positions={summary?.positions || []} loading={loadingSummary} />
          </div>
        </div>

        {/* Positions Table */}
        <PositionsTable
          positions={sortedPositions}
          onSort={handleSort}
          sortKey={sortKey}
          sortOrder={sortOrder}
          loading={loadingSummary}
        />

        {/* Rebalance Actions */}
        <RebalanceActions
          selectedStrategy={selectedStrategy}
          onStrategyChange={setSelectedStrategy}
          capitalAllocation={capitalAllocation}
          onCapitalChange={setCapitalAllocation}
          onRebalance={handleRebalance}
          rebalancing={rebalancing}
          availableCash={summary?.cash_balance || 0}
        />
      </div>
    </div>
  );
}

// ==================== PORTFOLIO SUMMARY CARDS ====================

interface PortfolioSummaryCardsProps {
  summary: PortfolioSummary | null;
  loading: boolean;
}

function PortfolioSummaryCards({ summary, loading }: PortfolioSummaryCardsProps) {
  const cards = [
    {
      title: 'Total Portfolio Value',
      value: summary?.total_value || 0,
      icon: Wallet,
      color: 'from-blue-500 to-cyan-600',
      bgColor: 'bg-blue-500/10',
      format: 'currency'
    },
    {
      title: 'Cash Balance',
      value: summary?.cash_balance || 0,
      icon: DollarSign,
      color: 'from-green-500 to-emerald-600',
      bgColor: 'bg-green-500/10',
      format: 'currency'
    },
    {
      title: 'Daily Change',
      value: summary?.daily_change_percent || 0,
      icon: summary?.daily_change_percent && summary.daily_change_percent >= 0 ? TrendingUp : TrendingDown,
      color: summary?.daily_change_percent && summary.daily_change_percent >= 0 ? 'from-green-500 to-emerald-600' : 'from-red-500 to-orange-600',
      bgColor: summary?.daily_change_percent && summary.daily_change_percent >= 0 ? 'bg-green-500/10' : 'bg-red-500/10',
      format: 'percentage'
    },
    {
      title: 'Active Positions',
      value: summary?.positions.length || 0,
      icon: BarChart3,
      color: 'from-purple-500 to-pink-600',
      bgColor: 'bg-purple-500/10',
      format: 'number'
    }
  ];

  const formatValue = (value: number, format: string) => {
    if (format === 'currency') {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    } else if (format === 'percentage') {
      return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
    }
    return value.toString();
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="relative group"
        >
          <Card className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6 hover:border-white/20 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10">
            {/* Icon */}
            <div className={`w-12 h-12 rounded-xl ${card.bgColor} flex items-center justify-center mb-4`}>
              <card.icon className="w-6 h-6" style={{ 
                background: `linear-gradient(to bottom right, ${card.color.split(' ')[1]}, ${card.color.split(' ')[3]})`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }} />
            </div>

            {/* Title */}
            <p className="text-sm text-gray-400 mb-2">{card.title}</p>

            {/* Value */}
            {loading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                <span className="text-gray-500">Loading...</span>
              </div>
            ) : (
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: index * 0.1 + 0.2, type: 'spring' }}
                className="text-2xl font-bold"
              >
                {formatValue(card.value, card.format)}
              </motion.div>
            )}
          </Card>
        </motion.div>
      ))}
    </div>
  );
}

// ==================== PERFORMANCE CHART ====================

interface PerformanceChartProps {
  data: PortfolioPerformance | null;
  timeframe: Timeframe;
  onTimeframeChange: (tf: Timeframe) => void;
  loading: boolean;
}

function PerformanceChart({ data, timeframe, onTimeframeChange, loading }: PerformanceChartProps) {
  const chartData = data
    ? data.dates.map((date, index) => ({
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        value: data.values[index]
      }))
    : [];

  // Sample data for better visualization
  const sampleRate = Math.ceil(chartData.length / 30);
  const sampledData = chartData.filter((_, index) => index % sampleRate === 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Portfolio Performance</h2>
          <p className="text-sm text-gray-400 mt-1">Historical value over time</p>
        </div>

        {/* Timeframe Selector */}
        <div className="flex gap-2">
          {(['1M', '3M', '6M', '1Y'] as Timeframe[]).map((tf) => (
            <button
              key={tf}
              onClick={() => onTimeframeChange(tf)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                timeframe === tf
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                  : 'bg-white/5 text-gray-400 hover:text-white hover:bg-white/10'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-[300px] flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={sampledData}>
            <defs>
              <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="date"
              stroke="#666"
              tick={{ fill: '#999', fontSize: 12 }}
            />
            <YAxis
              stroke="#666"
              tick={{ fill: '#999' }}
              tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(0,0,0,0.95)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px',
                backdropFilter: 'blur(20px)'
              }}
              labelStyle={{ color: '#fff', marginBottom: '8px' }}
              formatter={(value: number) => [
                `₹${value.toLocaleString('en-IN')}`,
                'Portfolio Value'
              ]}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={false}
              fill="url(#portfolioGradient)"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </motion.div>
  );
}

// ==================== ALLOCATION PIE CHART ====================

interface AllocationChartProps {
  positions: Position[];
  loading: boolean;
}

function AllocationChart({ positions, loading }: AllocationChartProps) {
  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

  const chartData = positions.map((pos, index) => ({
    name: pos.symbol,
    value: pos.allocation_percent || 0,
    color: COLORS[index % COLORS.length]
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6 h-full"
    >
      <div className="mb-6">
        <h2 className="text-xl font-bold">Portfolio Allocation</h2>
        <p className="text-sm text-gray-400 mt-1">Distribution by holdings</p>
      </div>

      {loading ? (
        <div className="h-[250px] flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : chartData.length === 0 ? (
        <div className="h-[250px] flex items-center justify-center text-gray-400">
          No positions to display
        </div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0,0,0,0.95)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px'
                }}
                formatter={(value: number) => `${value.toFixed(2)}%`}
              />
            </PieChart>
          </ResponsiveContainer>

          {/* Legend */}
          <div className="mt-4 space-y-2">
            {chartData.map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-gray-300">{item.name}</span>
                </div>
                <span className="text-gray-400">{item.value.toFixed(2)}%</span>
              </div>
            ))}
          </div>
        </>
      )}
    </motion.div>
  );
}

// ==================== POSITIONS TABLE ====================

interface PositionsTableProps {
  positions: Position[];
  onSort: (key: keyof Position) => void;
  sortKey: keyof Position;
  sortOrder: 'asc' | 'desc';
  loading: boolean;
}

function PositionsTable({ positions, onSort, sortKey, sortOrder, loading }: PositionsTableProps) {
  const SortIcon = ({ column }: { column: keyof Position }) => {
    if (sortKey !== column) return <ChevronDown className="w-4 h-4 text-gray-600" />;
    return sortOrder === 'asc' ? (
      <ArrowUpRight className="w-4 h-4 text-blue-400" />
    ) : (
      <ArrowDownRight className="w-4 h-4 text-blue-400" />
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
      className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6"
    >
      <div className="mb-6">
        <h2 className="text-xl font-bold">Current Positions</h2>
        <p className="text-sm text-gray-400 mt-1">Your active stock holdings</p>
      </div>

      {loading ? (
        <div className="h-[200px] flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th
                  className="text-left py-3 px-4 text-sm font-medium text-gray-400 cursor-pointer hover:text-white transition-colors"
                  onClick={() => onSort('symbol')}
                >
                  <div className="flex items-center gap-2">
                    Symbol <SortIcon column="symbol" />
                  </div>
                </th>
                <th
                  className="text-right py-3 px-4 text-sm font-medium text-gray-400 cursor-pointer hover:text-white transition-colors"
                  onClick={() => onSort('quantity')}
                >
                  <div className="flex items-center justify-end gap-2">
                    Quantity <SortIcon column="quantity" />
                  </div>
                </th>
                <th
                  className="text-right py-3 px-4 text-sm font-medium text-gray-400 cursor-pointer hover:text-white transition-colors"
                  onClick={() => onSort('current_price')}
                >
                  <div className="flex items-center justify-end gap-2">
                    Current Price <SortIcon column="current_price" />
                  </div>
                </th>
                <th
                  className="text-right py-3 px-4 text-sm font-medium text-gray-400 cursor-pointer hover:text-white transition-colors"
                  onClick={() => onSort('daily_change_percent')}
                >
                  <div className="flex items-center justify-end gap-2">
                    Change % <SortIcon column="daily_change_percent" />
                  </div>
                </th>
                <th
                  className="text-right py-3 px-4 text-sm font-medium text-gray-400 cursor-pointer hover:text-white transition-colors"
                  onClick={() => onSort('allocation_percent')}
                >
                  <div className="flex items-center justify-end gap-2">
                    Allocation % <SortIcon column="allocation_percent" />
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {positions.map((position, index) => (
                <motion.tr
                  key={position.symbol}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors"
                >
                  <td className="py-3 px-4 font-medium">{position.symbol}</td>
                  <td className="py-3 px-4 text-right">{position.quantity}</td>
                  <td className="py-3 px-4 text-right">
                    ₹{position.current_price.toLocaleString('en-IN')}
                  </td>
                  <td className={`py-3 px-4 text-right ${
                    position.daily_change_percent >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {position.daily_change_percent >= 0 ? '+' : ''}{position.daily_change_percent.toFixed(2)}%
                  </td>
                  <td className="py-3 px-4 text-right text-gray-400">
                    {position.allocation_percent?.toFixed(2)}%
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
}

// ==================== REBALANCE ACTIONS ====================

interface RebalanceActionsProps {
  selectedStrategy: ModelStrategy;
  onStrategyChange: (strategy: ModelStrategy) => void;
  capitalAllocation: string;
  onCapitalChange: (value: string) => void;
  onRebalance: () => void;
  rebalancing: boolean;
  availableCash: number;
}

function RebalanceActions({
  selectedStrategy,
  onStrategyChange,
  capitalAllocation,
  onCapitalChange,
  onRebalance,
  rebalancing,
  availableCash
}: RebalanceActionsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7 }}
      className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold">Portfolio Rebalancing</h2>
          <p className="text-sm text-gray-400">AI-powered portfolio optimization</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Strategy Selector */}
        <div>
          <label className="text-sm text-gray-400 mb-2 block">ML Model Strategy</label>
          <div className="relative">
            <select
              value={selectedStrategy}
              onChange={(e) => onStrategyChange(e.target.value as ModelStrategy)}
              className="w-full text-white appearance-none pl-4 pr-10 py-3 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                color: 'white'
              }}
            >
              <option value="LSTM" className="bg-gray-800 text-white">LSTM Neural Network</option>
              <option value="Linear" className="bg-gray-800 text-white">Linear Regression</option>
              <option value="Logistic" className="bg-gray-800 text-white">Logistic Regression</option>
              <option value="SVM" className="bg-gray-800 text-white">Support Vector Machine</option>
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        {/* Capital Allocation Input */}
        <div>
          <label className="text-sm text-gray-400 mb-2 block">
            Capital Allocation (Available: ₹{availableCash.toLocaleString('en-IN')})
          </label>
          <input
            type="number"
            value={capitalAllocation}
            onChange={(e) => onCapitalChange(e.target.value)}
            placeholder="Enter amount"
            className="w-full text-white placeholder:text-gray-500 px-4 py-3 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 focus:border-blue-500 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            disabled={rebalancing}
          />
        </div>

        {/* Rebalance Button */}
        <div className="flex items-end">
          <Button
            onClick={onRebalance}
            disabled={rebalancing || !capitalAllocation}
            className="w-full h-[48px] rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {rebalancing ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Rebalancing...
              </>
            ) : (
              <>
                <Activity className="w-5 h-5 mr-2" />
                Rebalance Portfolio
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-4 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
        <p className="text-sm text-blue-200">
          <strong>Note:</strong> The {selectedStrategy} model will analyze market conditions and rebalance your portfolio for optimal returns based on predicted stock movements.
        </p>
      </div>
    </motion.div>
  );
}
