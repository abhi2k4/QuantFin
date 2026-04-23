import { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
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
import { IconTrendingUp, IconTrendingDown, IconWallet, IconCurrencyDollar, IconActivity, IconRefresh, IconLoader, IconChevronDown, IconArrowUpRight, IconArrowDownRight, IconChartBar, IconSparkles, IconBrain, IconAlertCircle, IconEdit, IconX } from '@tabler/icons-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  getPortfolioSummary,
  getPortfolioPerformance,
  rebalancePortfolio,
  getStrategyComparison,
  updateCashBalance,
  getErrorMessage,
  type PortfolioSummary,
  type PortfolioPerformance,
  type Position,
  type RebalanceRequest,
  type AllocationRecommendation,
  type StrategyComparisonResponse
} from '@/services/api';
import { toast } from 'sonner';

type Timeframe = '1M' | '3M' | '6M' | '1Y';
type ModelStrategy = 'LSTM' | 'Linear' | 'Logistic' | 'SVM' | 'ARIMA';

export default function Dashboard() {
  // State management
  const navigate = useNavigate();
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [performance, setPerformance] = useState<PortfolioPerformance | null>(null);
  const [allocations, setAllocations] = useState<AllocationRecommendation[]>([]);
  const [portfolioMetrics, setPortfolioMetrics] = useState<{
    expected_return: number;
    expected_risk: number;
    sharpe_ratio?: number;
  } | null>(null);
  const [strategyComparison, setStrategyComparison] = useState<StrategyComparisonResponse | null>(null);
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
  
  // Cash balance edit state
  const [showCashBalanceDialog, setShowCashBalanceDialog] = useState(false);
  const [newCashBalance, setNewCashBalance] = useState<string>('');
  const [updatingCashBalance, setUpdatingCashBalance] = useState(false);
  const summaryLoadedRef = useRef(false);

  const loadPortfolioSummary = async (signal?: AbortSignal) => {
    setLoadingSummary(true);
    try {
      const data = await getPortfolioSummary(signal);
      // Calculate allocations
      const totalValue = data.positions.reduce((sum, pos) => sum + (pos.quantity * pos.current_price), 0);
      data.positions = data.positions.map(pos => ({
        ...pos,
        allocation: ((pos.quantity * pos.current_price) / totalValue) * 100
      }));
      setSummary(data);
    } catch (error) {
      if (signal?.aborted || (error as { code?: string; name?: string })?.code === 'ERR_CANCELED' || (error as { code?: string; name?: string })?.name === 'CanceledError') {
        return;
      }
      console.error('Error loading portfolio summary:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoadingSummary(false);
    }
  };

  const loadPortfolioPerformance = async (currentTimeframe: Timeframe, signal?: AbortSignal) => {
    setLoadingPerformance(true);
    try {
      const data = await getPortfolioPerformance(currentTimeframe, signal);
      setPerformance(data);
    } catch (error) {
      if (signal?.aborted || (error as { code?: string; name?: string })?.code === 'ERR_CANCELED' || (error as { code?: string; name?: string })?.name === 'CanceledError') {
        return;
      }
      console.error('Error loading portfolio performance:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoadingPerformance(false);
    }
  };

  const loadStrategyComparison = async (currentTimeframe: Timeframe, signal?: AbortSignal) => {
    try {
      const data = await getStrategyComparison(currentTimeframe, 100000, signal);
      setStrategyComparison(data);
    } catch (error) {
      if (signal?.aborted || (error as { code?: string; name?: string })?.code === 'ERR_CANCELED' || (error as { code?: string; name?: string })?.name === 'CanceledError') {
        return;
      }
      console.error('Error loading strategy comparison:', error);
      toast.error(getErrorMessage(error));
    }
  };

  useEffect(() => {
    const controller = new AbortController();

    const loadDashboardData = async () => {
      if (!summaryLoadedRef.current) {
        await loadPortfolioSummary(controller.signal);
        summaryLoadedRef.current = true;
      }

      await loadPortfolioPerformance(timeframe, controller.signal);
      await loadStrategyComparison(timeframe, controller.signal);
    };

    void loadDashboardData();

    return () => {
      controller.abort();
    };
  }, [timeframe]);
  
  const handleUpdateCashBalance = async () => {
    const amount = parseFloat(newCashBalance);
    
    if (isNaN(amount) || amount < 0) {
      toast.error('Please enter a valid positive amount');
      return;
    }
    
    setUpdatingCashBalance(true);
    try {
      const response = await updateCashBalance(amount);
      toast.success(response.message);
      setShowCashBalanceDialog(false);
      setNewCashBalance('');
      // Reload summary to show updated cash balance
      await loadPortfolioSummary();
    } catch (error) {
      console.error('Error updating cash balance:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setUpdatingCashBalance(false);
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
      
      // Update summary with rebalance results
      setSummary(result);
      
      // Store allocation recommendations and metrics
      if (result.allocations && result.allocations.length > 0) {
        setAllocations(result.allocations);
        setPortfolioMetrics({
          expected_return: result.expected_return,
          expected_risk: result.expected_risk,
          sharpe_ratio: result.sharpe_ratio
        });
      }
      
      toast.success(`Portfolio rebalanced successfully using ${selectedStrategy} strategy!`);
      setCapitalAllocation('');
      
      // Reload both summary and performance data
      await loadPortfolioSummary();
      await loadPortfolioPerformance(timeframe);
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
    <div className="min-h-screen bg-[#0d0d0d] text-white">
      {/* Top Bar */}
      <div className="border-b border-[rgba(255,255,255,0.06)] bg-[rgba(13,13,13,0.9)] backdrop-blur-xl">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Portfolio Dashboard</h1>
              <p className="text-sm text-gray-400 mt-1">Real-time portfolio management & insights</p>
            </div>
            <div className="flex gap-3">
              {/* <Button
                onClick={() => navigate('/analytics')}
                className="rounded-xl bg-[#c8ff00] text-[#0d0d0d] hover:bg-[#d8ff33] border-0 font-semibold"
              >
                <IconBrain className="w-4 h-4 mr-2" />
                ML Analytics
              </Button> */}
              <Button
                onClick={() => navigate('/backtest')}
                className="rounded-xl bg-[#c8ff00] text-black hover:bg-[#d8ff33] border-0"
              >
                <IconChartBar className="w-4 h-4 mr-2" />
                Backtesting
              </Button>
              <Button
                onClick={() => {
                  void loadPortfolioSummary();
                  void loadPortfolioPerformance(timeframe);
                  void loadStrategyComparison(timeframe);
                }}
                className="rounded-xl bg-[#1a1a1a] hover:bg-[#222] border border-[rgba(255,255,255,0.07)]"
              >
                <IconRefresh className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-6 py-8 space-y-8">
        {/* Portfolio Summary Cards */}
        <PortfolioSummaryCards 
          summary={summary} 
          loading={loadingSummary}
          onEditCashBalance={() => {
            setNewCashBalance(summary?.cash_balance.toString() || '0');
            setShowCashBalanceDialog(true);
          }}
        />

        {/* Your ML-Optimized Portfolio Section */}
        {allocations.length > 0 && portfolioMetrics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="bg-[#141414] border-[rgba(255,255,255,0.07)] p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-[rgba(200,255,0,0.1)] border border-[rgba(200,255,0,0.2)] rounded-lg">
                    <IconBrain className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">Your ML-Optimized Portfolio</h2>
                    <p className="text-sm text-gray-400">Powered by {selectedStrategy} Model • Top {allocations.length} Stocks</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-xs text-gray-400">Expected Return (Annual)</p>
                    <p className="text-2xl font-bold text-green-400">
                      {portfolioMetrics.expected_return.toFixed(2)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">Sharpe Ratio</p>
                    <p className="text-2xl font-bold text-[#c8ff00]">
                      {portfolioMetrics.sharpe_ratio?.toFixed(3) || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-4 gap-4 mb-6">
                <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
                  <div className="flex items-center gap-2 mb-2">
                    <IconWallet className="w-4 h-4 text-[#a0a0a0]" />
                    <span className="text-xs text-gray-400">Total Stocks</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{allocations.length}</p>
                </div>
                <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
                  <div className="flex items-center gap-2 mb-2">
                    <IconTrendingUp className="w-4 h-4 text-green-400" />
                    <span className="text-xs text-gray-400">Avg Confidence</span>
                  </div>
                  <p className="text-2xl font-bold text-green-400">
                    {(allocations.reduce((sum, a) => sum + a.confidence, 0) / allocations.length * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
                  <div className="flex items-center gap-2 mb-2">
                    <IconActivity className="w-4 h-4 text-[#f97316]" />
                    <span className="text-xs text-gray-400">Risk Level</span>
                  </div>
                  <p className="text-2xl font-bold text-[#f97316]">
                    {portfolioMetrics.expected_risk.toFixed(2)}%
                  </p>
                </div>
                <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
                  <div className="flex items-center gap-2 mb-2">
                    <IconSparkles className="w-4 h-4 text-[#eab308]" />
                    <span className="text-xs text-gray-400">Model</span>
                  </div>
                  <p className="text-lg font-bold text-white">{selectedStrategy}</p>
                </div>
              </div>

              {/* Top Holdings Preview */}
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-gray-400 mb-3">Top 5 Holdings</h3>
                {allocations.slice(0, 5).map((allocation, index) => (
                  <motion.div
                    key={allocation.symbol}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/5 hover:border-white/20 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 bg-[rgba(200,255,0,0.12)] border border-[rgba(200,255,0,0.3)] rounded text-[#c8ff00] font-bold text-sm">
                        #{index + 1}
                      </div>
                      <div>
                        <p className="font-semibold text-white">{allocation.symbol}</p>
                        <p className="text-xs text-gray-400">
                          {allocation.quantity} shares @ ₹{allocation.buy_price.toFixed(2)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-white">
                        ₹{allocation.allocation_amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                      </p>
                      <div className="flex items-center gap-1 justify-end">
                        <span className="text-xs text-gray-400">{allocation.weight_percent.toFixed(1)}%</span>
                        <span className={`text-xs ${allocation.predicted_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          ({allocation.predicted_return >= 0 ? '+' : ''}{allocation.predicted_return.toFixed(2)}%)
                        </span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* View Full Portfolio Button */}
              <div className="mt-4 pt-4 border-t border-white/10">
                <p className="text-xs text-center text-gray-400">
                  Scroll down to see complete allocation table with all {allocations.length} stocks and detailed metrics
                </p>
              </div>
            </Card>
          </motion.div>
        )}

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

        {/* Allocation Table - Display ML-based stock recommendations */}
        {allocations.length > 0 && portfolioMetrics && (
          <AllocationTable
            allocations={allocations}
            metrics={portfolioMetrics}
            strategy={selectedStrategy}
          />
        )}

        {/* Strategy Comparison - All models vs Nifty50 */}
        {strategyComparison && (
          <>
            <StrategyComparisonChart
              data={strategyComparison}
              timeframe={timeframe}
              onTimeframeChange={setTimeframe}
            />
            
            {/* Individual Model Charts */}
            <IndividualModelCharts
              data={strategyComparison}
              timeframe={timeframe}
            />
          </>
        )}
      </div>
      
      {/* Cash Balance Edit Dialog */}
      {showCashBalanceDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-[#141414] rounded-xl border border-[rgba(255,255,255,0.08)] p-6 w-full max-w-md mx-4"
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-white">Update Cash Balance</h3>
                <p className="text-sm text-gray-400 mt-1">Enter your available cash for investment</p>
              </div>
              <button
                onClick={() => setShowCashBalanceDialog(false)}
                className="p-2 rounded-lg hover:bg-[rgba(200,255,0,0.03)] transition-colors"
              >
                <IconX className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Cash Balance (₹)
                </label>
                <input
                  type="number"
                  value={newCashBalance}
                  onChange={(e) => setNewCashBalance(e.target.value)}
                  placeholder="Enter amount"
                  className="w-full px-4 py-3 rounded-lg bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-[#c8ff00]/30 focus:border-transparent"
                  min="0"
                  step="1000"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Current balance: ₹{new Intl.NumberFormat('en-IN').format(summary?.cash_balance || 0)}
                </p>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowCashBalanceDialog(false)}
                  className="flex-1 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateCashBalance}
                  disabled={updatingCashBalance}
                  className="flex-1 px-4 py-3 rounded-xl bg-[#c8ff00] hover:bg-[#d8ff33] text-black font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {updatingCashBalance ? (
                    <>
                      <IconLoader className="w-4 h-4 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    'Update Balance'
                  )}
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}

// ==================== PORTFOLIO SUMMARY CARDS ====================

interface PortfolioSummaryCardsProps {
  summary: PortfolioSummary | null;
  loading: boolean;
  onEditCashBalance: () => void;
}

function PortfolioSummaryCards({ summary, loading, onEditCashBalance }: PortfolioSummaryCardsProps) {
  const cards = [
    {
      title: 'Total Portfolio Value',
      value: summary?.total_value || 0,
      icon: IconWallet,
      color: '#c8ff00',
      bgColor: 'bg-[rgba(200,255,0,0.06)]',
      format: 'currency'
    },
    {
      title: 'Cash Balance',
      value: summary?.cash_balance || 0,
      icon: IconCurrencyDollar,
      color: '#c8ff00',
      bgColor: 'bg-[rgba(200,255,0,0.06)]',
      format: 'currency'
    },
    {
      title: 'Daily Change',
      value: summary?.daily_change_percent || 0,
      icon: summary?.daily_change_percent && summary.daily_change_percent >= 0 ? IconTrendingUp : IconTrendingDown,
      color: summary?.daily_change_percent && summary.daily_change_percent >= 0 ? '#c8ff00' : '#f87171',
      bgColor: summary?.daily_change_percent && summary.daily_change_percent >= 0 ? 'bg-[rgba(200,255,0,0.06)]' : 'bg-[rgba(248,113,113,0.08)]',
      format: 'percentage'
    },
    {
      title: 'Active Positions',
      value: summary?.positions.length || 0,
      icon: IconChartBar,
      color: '#c8ff00',
      bgColor: 'bg-[rgba(200,255,0,0.06)]',
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
          <Card className="rounded-xl bg-[#141414] border border-[rgba(255,255,255,0.07)] p-6 hover:border-white/20 transition-all duration-300 hover:border-[rgba(200,255,0,0.15)]">
            {/* Edit button for Cash Balance */}
            {card.title === 'Cash Balance' && !loading && (
              <button
                onClick={onEditCashBalance}
                className="absolute top-4 right-4 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-200 opacity-0 group-hover:opacity-100"
                title="Edit Cash Balance"
              >
                <IconEdit className="w-4 h-4 text-gray-400 hover:text-white" />
              </button>
            )}
            
            {/* Icon */}
            <div className={`w-12 h-12 rounded-xl ${card.bgColor} flex items-center justify-center mb-4`}>
              <card.icon className="w-6 h-6 text-[#c8ff00]" />
            </div>

            {/* Title */}
            <p className="text-sm text-gray-400 mb-2">{card.title}</p>

            {/* Value */}
            {loading ? (
              <div className="flex items-center gap-2">
                <IconLoader className="w-5 h-5 animate-spin text-[#c8ff00]" />
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
  const chartData = data?.data || [];
  const metrics = data?.metrics;
  
  // Sample data for better visualization on large datasets
  const sampleRate = Math.max(1, Math.ceil(chartData.length / 50));
  const sampledData = chartData.filter((_, index) => index % sampleRate === 0);
  
  // Format chart data
  const formattedChartData = sampledData.map((item) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    fullDate: item.date,
    value: item.value
  }));
  
  // Calculate daily change for tooltip
  const dataWithChanges = formattedChartData.map((item, index) => {
    if (index === 0) return { ...item, change: 0 };
    const prevValue = formattedChartData[index - 1].value;
    const change = ((item.value - prevValue) / prevValue) * 100;
    return { ...item, change };
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="rounded-xl bg-[#141414] border border-[rgba(255,255,255,0.07)] p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Portfolio Performance</h2>
          <p className="text-sm text-gray-400 mt-1">Historical value with real market data</p>
        </div>

        {/* Timeframe Selector */}
        <div className="flex gap-2">
          {(['1M', '3M', '6M', '1Y'] as Timeframe[]).map((tf) => (
            <button
              key={tf}
              onClick={() => onTimeframeChange(tf)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                timeframe === tf
                  ? 'bg-[#c8ff00] text-[#0d0d0d] font-semibold'
                  : 'bg-white/5 text-gray-400 hover:text-white hover:bg-white/10'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Warnings */}
      {data?.warnings && data.warnings.length > 0 && (
        <div className="mb-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 flex items-start gap-2">
          <IconAlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-yellow-200">
            {data.warnings.map((warning, idx) => (
              <div key={idx}>{warning}</div>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <div className="h-[350px] flex items-center justify-center">
          <IconLoader className="w-8 h-8 animate-spin text-[#c8ff00]" />
        </div>
      ) : !data || chartData.length === 0 ? (
        <div className="h-[350px] flex items-center justify-center text-gray-400">
          <div className="text-center">
            <IconActivity className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No performance data available</p>
          </div>
        </div>
      ) : (
        <>
          {/* Performance Metrics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[rgba(255,255,255,0.07)]">
              <p className="text-xs text-gray-400 mb-1">Initial Value</p>
              <p className="text-lg font-bold">₹{metrics?.initial_value.toLocaleString('en-IN')}</p>
            </div>
            <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[rgba(255,255,255,0.07)]">
              <p className="text-xs text-gray-400 mb-1">Final Value</p>
              <p className="text-lg font-bold">₹{metrics?.final_value.toLocaleString('en-IN')}</p>
            </div>
            <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[rgba(255,255,255,0.07)]">
              <p className="text-xs text-gray-400 mb-1">Total Return</p>
              <p className={`text-lg font-bold flex items-center gap-1 ${
                (metrics?.total_return || 0) >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {(metrics?.total_return || 0) >= 0 ? <IconArrowUpRight className="w-4 h-4" /> : <IconArrowDownRight className="w-4 h-4" />}
                {metrics?.total_return.toFixed(2)}%
              </p>
            </div>
            <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[rgba(255,255,255,0.07)]">
              <p className="text-xs text-gray-400 mb-1">Volatility</p>
              <p className="text-lg font-bold">{metrics?.volatility.toFixed(2)}%</p>
            </div>
            <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[rgba(255,255,255,0.07)]">
              <p className="text-xs text-gray-400 mb-1">Sharpe Ratio</p>
              <p className="text-lg font-bold">{metrics?.sharpe_ratio.toFixed(2)}</p>
            </div>
            <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[rgba(255,255,255,0.07)]">
              <p className="text-xs text-gray-400 mb-1">Max Drawdown</p>
              <p className="text-lg font-bold text-red-400">{metrics?.max_drawdown.toFixed(2)}%</p>
            </div>
          </div>

          {/* Chart */}
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={dataWithChanges}>
              <defs>
                <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#c8ff00" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#c8ff00" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
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
                  backgroundColor: '#0d0d0d',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: '12px',
                  backdropFilter: 'blur(20px)',
                  padding: '12px'
                }}
                labelStyle={{ color: '#fff', marginBottom: '8px', fontWeight: 'bold' }}
                formatter={(value: number, name: string, props: any) => {
                  if (name === 'value') {
                    const change = props.payload.change;
                    return [
                      <div key="tooltip" className="space-y-1">
                        <div className="text-white font-bold">₹{value.toLocaleString('en-IN')}</div>
                        {change !== 0 && (
                          <div className={`text-sm ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {change >= 0 ? '↑' : '↓'} {Math.abs(change).toFixed(2)}%
                          </div>
                        )}
                      </div>,
                      'Portfolio Value'
                    ];
                  }
                  return [value, name];
                }}
                labelFormatter={(label) => {
                  const item = dataWithChanges.find(d => d.date === label);
                  return item?.fullDate || label;
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#c8ff00"
                strokeWidth={2}
                fill="url(#portfolioGradient)"
                fillOpacity={1}
              />
            </AreaChart>
          </ResponsiveContainer>

          {/* Data points info */}
          <p className="text-xs text-gray-500 mt-4 text-center">
            Showing {chartData.length} trading days • Last updated: {new Date().toLocaleString()}
          </p>
        </>
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
  const COLORS = ['#c8ff00', '#a0a0a0', '#34d399', '#f59e0b', '#f87171', '#60a5fa'];

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
      className="rounded-xl bg-[#141414] border border-[rgba(255,255,255,0.07)] p-6 h-full"
    >
      <div className="mb-6">
        <h2 className="text-xl font-bold">Portfolio Allocation</h2>
        <p className="text-sm text-gray-400 mt-1">Distribution by holdings</p>
      </div>

      {loading ? (
        <div className="h-[250px] flex items-center justify-center">
          <IconLoader className="w-8 h-8 animate-spin text-[#c8ff00]" />
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
                  backgroundColor: '#0d0d0d',
                  border: '1px solid rgba(255,255,255,0.08)',
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
    if (sortKey !== column) return <IconChevronDown className="w-4 h-4 text-gray-600" />;
    return sortOrder === 'asc' ? (
      <IconArrowUpRight className="w-4 h-4 text-[#c8ff00]" />
    ) : (
      <IconArrowDownRight className="w-4 h-4 text-red-400" />
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
      className="rounded-xl bg-[#141414] border border-[rgba(255,255,255,0.07)] p-6"
    >
      <div className="mb-6">
        <h2 className="text-xl font-bold">Current Positions</h2>
        <p className="text-sm text-gray-400 mt-1">Your active stock holdings</p>
      </div>

      {loading ? (
        <div className="h-[200px] flex items-center justify-center">
          <IconLoader className="w-8 h-8 animate-spin text-[#c8ff00]" />
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
                  className="border-b border-white/5 hover:bg-[rgba(200,255,0,0.03)] transition-colors"
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
      className="rounded-xl bg-[#141414] border border-[rgba(255,255,255,0.07)] p-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-[rgba(200,255,0,0.08)] border border-[rgba(200,255,0,0.2)] flex items-center justify-center">
          <IconSparkles className="w-5 h-5" />
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
              className="w-full text-white appearance-none pl-4 pr-10 py-3 rounded-lg bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] hover:border-[rgba(200,255,0,0.2)] transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#c8ff00]/30/50"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                color: 'white'
              }}
            >
              <option value="LSTM" className="bg-gray-800 text-white">LSTM Neural Network</option>
              <option value="Linear" className="bg-gray-800 text-white">Linear Regression</option>
              <option value="Logistic" className="bg-gray-800 text-white">Logistic Regression</option>
              <option value="SVM" className="bg-gray-800 text-white">Support Vector Machine</option>
              <option value="ARIMA" className="bg-gray-800 text-white">ARIMA Time Series</option>
            </select>
            <IconChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
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
            className="w-full text-white placeholder:text-gray-600 px-4 py-3 rounded-lg bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] hover:border-[rgba(200,255,0,0.2)] focus:border-[#c8ff00] transition-all focus:outline-none focus:ring-2 focus:ring-[#c8ff00]/30/50"
            disabled={rebalancing}
          />
        </div>

        {/* Rebalance Button */}
        <div className="flex items-end">
          <Button
            onClick={onRebalance}
            disabled={rebalancing || !capitalAllocation}
            className="w-full h-[48px] rounded-xl bg-[#c8ff00] hover:bg-[#d8ff33] text-white font-medium transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {rebalancing ? (
              <>
                <IconLoader className="w-5 h-5 mr-2 animate-spin" />
                Rebalancing...
              </>
            ) : (
              <>
                <IconActivity className="w-5 h-5 mr-2" />
                Rebalance Portfolio
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-4 p-4 rounded-lg bg-[rgba(200,255,0,0.04)] border border-[rgba(200,255,0,0.15)]">
        <p className="text-sm text-[rgba(200,255,0,0.75)]">
          <strong>Note:</strong> The {selectedStrategy} model will analyze market conditions and rebalance your portfolio for optimal returns based on predicted stock movements.
        </p>
      </div>
    </motion.div>
  );
}

// ==================== ALLOCATION TABLE ====================

interface AllocationTableProps {
  allocations: AllocationRecommendation[];
  metrics: {
    expected_return: number;
    expected_risk: number;
    sharpe_ratio?: number;
  };
  strategy: ModelStrategy;
}

function AllocationTable({ allocations, metrics, strategy }: AllocationTableProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full"
    >
      <Card className="p-6 bg-[#141414] border-[rgba(255,255,255,0.07)]">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h3 className="text-2xl font-bold text-white flex items-center gap-2">
              <IconSparkles className="w-6 h-6 text-[#a0a0a0]" />
              Allocation Recommendations
            </h3>
            <p className="text-gray-400 text-sm mt-1">
              Based on {strategy} model predictions
            </p>
          </div>
          
          {/* Metrics Display */}
          <div className="flex flex-wrap gap-4">
            <div className="text-center">
              <p className="text-xs text-gray-400">Expected Return</p>
              <p className="text-lg font-bold text-green-400">
                {metrics.expected_return.toFixed(2)}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-400">Expected Risk</p>
              <p className="text-lg font-bold text-[#f97316]">
                {metrics.expected_risk.toFixed(2)}%
              </p>
            </div>
            {metrics.sharpe_ratio && (
              <div className="text-center">
                <p className="text-xs text-gray-400">Sharpe Ratio</p>
                <p className="text-lg font-bold text-[#c8ff00]">
                  {metrics.sharpe_ratio.toFixed(2)}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Stock</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Weight %</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Allocation</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Qty</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Buy Price</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Predicted Price</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Predicted Return</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Confidence</th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-300">Action</th>
              </tr>
            </thead>
            <tbody>
              {allocations.map((allocation, index) => (
                <motion.tr
                  key={allocation.symbol}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-gray-700/50 hover:bg-gray-700/20 transition-colors"
                >
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-[rgba(200,255,0,0.12)] border border-[rgba(200,255,0,0.3)] flex items-center justify-center text-[#c8ff00] text-xs font-bold">
                        {allocation.symbol.substring(0, 2)}
                      </div>
                      <span className="text-white font-medium">{allocation.symbol}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-right text-white font-medium">
                    {allocation.weight_percent.toFixed(2)}%
                  </td>
                  <td className="px-4 py-4 text-right text-white font-medium">
                    ₹{allocation.allocation_amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="px-4 py-4 text-right text-gray-300">
                    {allocation.quantity}
                  </td>
                  <td className="px-4 py-4 text-right text-gray-300">
                    ₹{allocation.buy_price.toFixed(2)}
                  </td>
                  <td className="px-4 py-4 text-right text-[#c8ff00]">
                    ₹{allocation.predicted_price.toFixed(2)}
                  </td>
                  <td className="px-4 py-4 text-right">
                    <span className={`font-semibold ${
                      allocation.predicted_return >= 10 ? 'text-green-400' :
                      allocation.predicted_return >= 5 ? 'text-green-300' :
                      allocation.predicted_return > 0 ? 'text-[#eab308]' :
                      'text-red-400'
                    }`}>
                      {allocation.predicted_return >= 0 ? '+' : ''}{allocation.predicted_return.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all ${
                            allocation.confidence >= 0.8 ? 'bg-[#c8ff00]' :
                            allocation.confidence >= 0.6 ? 'bg-[#c8ff00]/70' :
                            'bg-yellow-500'
                          }`}
                          style={{ width: `${allocation.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400 w-10 text-right">
                        {(allocation.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex justify-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        allocation.action === 'BUY' ? 'bg-[rgba(200,255,0,0.12)] text-[#c8ff00] border border-[rgba(200,255,0,0.3)]' :
                        allocation.action === 'HOLD' ? 'bg-[rgba(255,255,255,0.05)] text-[#a0a0a0] border border-[rgba(255,255,255,0.1)]' :
                        'bg-red-500/20 text-red-400 border border-red-500/50'
                      }`}>
                        {allocation.action}
                      </span>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Summary */}
        <div className="mt-6 pt-4 border-t border-gray-700">
          <div className="flex flex-wrap gap-4 justify-between items-center">
            <div className="text-gray-400 text-sm">
              <span className="font-semibold text-white">{allocations.length}</span> stocks recommended • 
              <span className="ml-2">Total Allocation: </span>
              <span className="font-semibold text-white">
                ₹{allocations.reduce((sum, a) => sum + a.allocation_amount, 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
              </span>
            </div>
            <div className="text-xs text-gray-500">
              * Predictions based on {strategy} model analysis
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}

// ==================== STRATEGY COMPARISON CHART ====================

interface StrategyComparisonChartProps {
  data: StrategyComparisonResponse;
  timeframe: string;
  onTimeframeChange: (timeframe: Timeframe) => void;
}

function StrategyComparisonChart({ data, timeframe, onTimeframeChange }: StrategyComparisonChartProps) {
  const [selectedStrategies, setSelectedStrategies] = useState<string[]>(['LSTM', 'NIFTY50']);
  
  // Get colors for each strategy
  const strategyColors: Record<string, string> = {
    'LSTM': '#c8ff00',      // Purple
    'Linear': '#a0a0a0',    // Blue
    'SVM': '#34d399',       // Green
    'ARIMA': '#f59e0b',     // Orange
    'NIFTY50': '#f87171'    // Red
  };

  // Prepare chart data
  const chartData = useMemo(() => {
    const strategies = data.strategies;
    const base =
      strategies.LSTM ||
      strategies.NIFTY50 ||
      Object.values(strategies).find((s) => s?.dates && s.values);
    if (!base?.dates) return [];

    const dates = base.dates;
    return dates.map((date, index) => {
      const point: any = { date };
      
      Object.entries(strategies).forEach(([name, strategy]) => {
        if (strategy && selectedStrategies.includes(name)) {
          point[name] = strategy.values[index];
        }
      });
      
      return point;
    });
  }, [data, selectedStrategies]);

  const toggleStrategy = (strategy: string) => {
    setSelectedStrategies(prev => 
      prev.includes(strategy)
        ? prev.filter(s => s !== strategy)
        : [...prev, strategy]
    );
  };

  // Calculate best performing strategy
  const bestStrategy = useMemo(() => {
    let best = { name: '', return: -Infinity };
    Object.entries(data.strategies).forEach(([name, strategy]) => {
      if (strategy && name !== 'NIFTY50' && strategy.total_return > best.return) {
        best = { name, return: strategy.total_return };
      }
    });
    return best;
  }, [data]);

  // Calculate outperformance vs Nifty50
  const outperformance = useMemo(() => {
    const nifty = data.strategies.NIFTY50;
    if (!nifty) return {};
    
    const results: Record<string, number> = {};
    Object.entries(data.strategies).forEach(([name, strategy]) => {
      if (strategy && name !== 'NIFTY50') {
        results[name] = strategy.total_return - nifty.total_return;
      }
    });
    return results;
  }, [data]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full mt-6"
    >
      <Card className="p-6 bg-[#141414] border-[rgba(255,255,255,0.07)]">
        {/* Header */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-white flex items-center gap-2">
              <IconChartBar className="w-6 h-6 text-[#c8ff00]" />
              Strategy Performance Comparison
            </h3>
            <p className="text-gray-400 text-sm mt-1">
              All ML models vs Nifty50 benchmark • {timeframe} period
            </p>
          </div>
          
          <div className="flex flex-wrap items-center gap-4">
            {/* Timeframe Selector */}
            <div className="flex gap-2">
              {(['1M', '3M', '6M', '1Y'] as Timeframe[]).map((tf) => (
                <button
                  key={tf}
                  onClick={() => onTimeframeChange(tf)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    timeframe === tf
                      ? 'bg-[#c8ff00] text-[#0d0d0d] font-semibold'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
            
            {/* Best Strategy Badge */}
            {bestStrategy.name && (
              <div className="px-4 py-2 rounded-lg bg-[rgba(200,255,0,0.06)] border border-[rgba(200,255,0,0.2)]">
                <p className="text-xs text-gray-400">Best Performer</p>
                <p className="text-lg font-bold text-[#c8ff00]"> {bestStrategy.name} • +{bestStrategy.return.toFixed(2)}%
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Strategy Toggle Buttons */}
        <div className="flex flex-wrap gap-2 mb-6">
          {Object.entries(data.strategies).map(([name, strategy]) => {
            if (!strategy) return null;
            const isSelected = selectedStrategies.includes(name);
            const color = strategyColors[name];
            
            return (
              <button
                key={name}
                onClick={() => toggleStrategy(name)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  isSelected
                    ? 'bg-opacity-20 border-2'
                    : 'bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] opacity-50 hover:opacity-100'
                }`}
                style={{
                  backgroundColor: isSelected ? `${color}20` : undefined,
                  borderColor: isSelected ? color : undefined,
                  color: isSelected ? color : '#9ca3af'
                }}
              >
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: color }}
                  />
                  <span>{name}</span>
                  <span className="text-xs">
                    {strategy.total_return >= 0 ? '+' : ''}{strategy.total_return.toFixed(1)}%
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Performance Chart */}
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis 
                dataKey="date" 
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              <YAxis 
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a1a',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={(value: any) => [`₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`, '']}
                labelFormatter={(label) => new Date(label).toLocaleDateString()}
              />
              
              {selectedStrategies.map(strategy => (
                <Line
                  key={strategy}
                  type="monotone"
                  dataKey={strategy}
                  stroke={strategyColors[strategy]}
                  strokeWidth={strategy === 'NIFTY50' ? 3 : 2}
                  dot={false}
                  name={strategy}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Metrics Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 mt-6">
          {Object.entries(data.strategies).map(([name, strategy]) => {
            if (!strategy) return null;
            const outperf = outperformance[name];
            
            return (
              <div
                key={name}
                className="p-4 rounded-xl bg-[#1a1a1a] border border-[rgba(255,255,255,0.07)] hover:border-[rgba(200,255,0,0.2)] transition-all"
              >
                <div className="flex items-center gap-2 mb-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: strategyColors[name] }}
                  />
                  <span className="text-sm font-semibold text-white">{name}</span>
                </div>
                
                <div className="space-y-1">
                  <div>
                    <p className="text-xs text-gray-400">Total Return</p>
                    <p className={`text-lg font-bold ${
                      strategy.total_return >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {strategy.total_return >= 0 ? '+' : ''}{strategy.total_return.toFixed(2)}%
                    </p>
                  </div>
                  
                  {outperf !== undefined && (
                    <div>
                      <p className="text-xs text-gray-400">vs Nifty50</p>
                      <p className={`text-sm font-semibold ${
                        outperf >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {outperf >= 0 ? '+' : ''}{outperf.toFixed(2)}%
                      </p>
                    </div>
                  )}
                  
                  {strategy.sharpe_ratio !== undefined && (
                    <div>
                      <p className="text-xs text-gray-400">Sharpe</p>
                      <p className="text-sm font-semibold text-blue-400">
                        {strategy.sharpe_ratio.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Summary */}
        <div className="mt-6 pt-4 border-t border-gray-700">
          <div className="flex flex-wrap gap-6 justify-between items-center">
            <div className="text-sm text-gray-400">
              <span className="font-semibold text-white">Initial Capital:</span> ₹{data.initial_capital.toLocaleString('en-IN')} • 
              <span className="ml-2 font-semibold text-white">Period:</span> {timeframe}
            </div>
            {data.strategies.NIFTY50 && (
              <div className="text-sm">
                <span className="text-gray-400">Nifty50 Benchmark: </span>
                <span className={`font-semibold ${
                  data.strategies.NIFTY50.total_return >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {data.strategies.NIFTY50.total_return >= 0 ? '+' : ''}{data.strategies.NIFTY50.total_return.toFixed(2)}%
                </span>
              </div>
            )}
          </div>
        </div>
      </Card>
    </motion.div>
  );
}

// ==================== INDIVIDUAL MODEL CHARTS ====================

interface IndividualModelChartsProps {
  data: StrategyComparisonResponse;
  timeframe: string;
}

function IndividualModelCharts({ data, timeframe }: IndividualModelChartsProps) {
  const models: Array<'LSTM' | 'Linear' | 'SVM' | 'ARIMA'> = ['LSTM', 'Linear', 'SVM', 'ARIMA'];
  
  const modelColors: Record<string, string> = {
    'LSTM': '#8b5cf6',
    'Linear': '#3b82f6',
    'SVM': '#10b981',
    'ARIMA': '#f59e0b',
    'NIFTY50': '#ef4444'
  };

  const modelDescriptions: Record<string, string> = {
    'LSTM': 'Long Short-Term Memory neural network - Best for capturing complex time series patterns',
    'Linear': 'Linear Regression - Effective for identifying stable linear trends',
    'SVM': 'Support Vector Machine - Excels at non-linear pattern recognition',
    'ARIMA': 'AutoRegressive Integrated Moving Average - Traditional statistical forecasting'
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      {models.map((model) => {
        const modelData = data.strategies[model];
        const niftyData = data.strategies.NIFTY50;
        
        if (!modelData || !niftyData) return null;

        // Prepare chart data comparing this model vs Nifty50
        const chartData = modelData.dates.map((date, index) => ({
          date,
          [model]: modelData.values[index],
          'NIFTY50': niftyData.values[index]
        }));

        const outperformance = modelData.total_return - niftyData.total_return;

        return (
          <motion.div
            key={model}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: models.indexOf(model) * 0.1 }}
          >
            <Card className="p-6 bg-[#141414] border-[rgba(255,255,255,0.07)] hover:border-gray-600/50 transition-all">
              {/* Model Header */}
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <div 
                      className="w-4 h-4 rounded-full" 
                      style={{ backgroundColor: modelColors[model] }}
                    />
                    <h4 className="text-xl font-bold text-white">{model} Model</h4>
                  </div>
                  <p className="text-xs text-gray-400">{modelDescriptions[model]}</p>
                </div>
                
                {/* Outperformance Badge */}
                <div className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                  outperformance >= 0
                    ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                    : 'bg-red-500/20 text-red-400 border border-red-500/50'
                }`}>
                  {outperformance >= 0 ? '+' : ''}{outperformance.toFixed(2)}% vs Nifty50
                </div>
              </div>

              {/* Chart */}
              <div className="h-[250px] w-full mb-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis 
                      dataKey="date" 
                      stroke="#9ca3af"
                      tick={{ fill: '#9ca3af', fontSize: 10 }}
                      tickFormatter={(value) => {
                        const date = new Date(value);
                        return `${date.getMonth() + 1}/${date.getDate()}`;
                      }}
                    />
                    <YAxis 
                      stroke="#9ca3af"
                      tick={{ fill: '#9ca3af', fontSize: 10 }}
                      tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a1a',
                        border: '1px solid rgba(255,255,255,0.08)',
                        borderRadius: '8px',
                        color: '#fff',
                        fontSize: '12px'
                      }}
                      formatter={(value: any) => [`₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`, '']}
                      labelFormatter={(label) => new Date(label).toLocaleDateString()}
                    />
                    
                    <Line
                      type="monotone"
                      dataKey={model}
                      stroke={modelColors[model]}
                      strokeWidth={3}
                      dot={false}
                      name={model}
                    />
                    <Line
                      type="monotone"
                      dataKey="NIFTY50"
                      stroke={modelColors['NIFTY50']}
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      dot={false}
                      name="Nifty50"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-gray-700/30">
                  <p className="text-xs text-gray-400 mb-1">{model} Return</p>
                  <p className={`text-xl font-bold ${
                    modelData.total_return >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {modelData.total_return >= 0 ? '+' : ''}{modelData.total_return.toFixed(2)}%
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-gray-700/30">
                  <p className="text-xs text-gray-400 mb-1">Nifty50 Return</p>
                  <p className={`text-xl font-bold ${
                    niftyData.total_return >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {niftyData.total_return >= 0 ? '+' : ''}{niftyData.total_return.toFixed(2)}%
                  </p>
                </div>
                {modelData.sharpe_ratio !== undefined && (
                  <>
                    <div className="p-3 rounded-lg bg-gray-700/30">
                      <p className="text-xs text-gray-400 mb-1">Sharpe Ratio</p>
                      <p className="text-xl font-bold text-blue-400">
                        {modelData.sharpe_ratio.toFixed(2)}
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-gray-700/30">
                      <p className="text-xs text-gray-400 mb-1">Risk</p>
                      <p className="text-xl font-bold text-[#f97316]">
                        {modelData.expected_risk?.toFixed(2)}%
                      </p>
                    </div>
                  </>
                )}
              </div>

              {/* Top Stocks */}
              {modelData.top_stocks && modelData.top_stocks.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-700">
                  <p className="text-xs text-gray-400 mb-2">Top Holdings:</p>
                  <div className="flex flex-wrap gap-2">
                    {modelData.top_stocks.map((stock) => (
                      <span
                        key={stock}
                        className="px-2 py-1 rounded bg-gray-700 text-white text-xs font-medium"
                      >
                        {stock}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
}

// ==================== PREDICTED VS ACTUAL CHART ====================

interface PredictedVsActualChartProps {
  data: PredictedVsActualResponse;
  loading: boolean;
}

function PredictedVsActualChart({ data, loading }: PredictedVsActualChartProps) {
  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl bg-[#141414] border border-[rgba(255,255,255,0.07)] p-6"
      >
        <div className="h-[400px] flex items-center justify-center">
          <IconLoader className="w-8 h-8 animate-spin text-[#c8ff00]" />
        </div>
      </motion.div>
    );
  }

  // Format data for chart
  const chartData = data.dates.map((date, index) => ({
    date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    fullDate: date,
    actual: data.actual_values[index],
    predicted: data.predicted_values[index],
    nifty50: data.nifty50_values[index]
  }));

  // Sample data for better performance (show every Nth point)
  const sampleRate = Math.max(1, Math.ceil(chartData.length / 60));
  const sampledData = chartData.filter((_, index) => index % sampleRate === 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="rounded-xl bg-[#141414] border border-[rgba(255,255,255,0.07)] p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Portfolio Performance: Predicted vs Actual</h2>
          <p className="text-sm text-gray-400 mt-1">
            ML predictions vs actual returns vs Nifty50 benchmark ({data.timeframe_days} days)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <IconBrain className="w-5 h-5 text-[#c8ff00]" />
          <span className="text-sm font-semibold text-blue-400">{data.strategy} Model</span>
        </div>
      </div>

      {/* Performance Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-[#141414] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
          <div className="flex items-center gap-2 mb-2">
            <IconTrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-xs text-gray-400">Actual Return</span>
          </div>
          <p className="text-2xl font-bold text-green-400">
            {data.returns.actual >= 0 ? '+' : ''}{data.returns.actual.toFixed(2)}%
          </p>
          <p className="text-xs text-gray-400 mt-1">
            ₹{data.final_values.actual.toLocaleString('en-IN')}
          </p>
        </div>

        <div className="bg-[#141414] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
          <div className="flex items-center gap-2 mb-2">
            <IconSparkles className="w-4 h-4 text-blue-400" />
            <span className="text-xs text-gray-400">Predicted Return</span>
          </div>
          <p className="text-2xl font-bold text-[#c8ff00]">
            {data.returns.predicted >= 0 ? '+' : ''}{data.returns.predicted.toFixed(2)}%
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Accuracy: {data.returns.prediction_accuracy.toFixed(1)}%
          </p>
        </div>

        <div className="bg-[#141414] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
          <div className="flex items-center gap-2 mb-2">
            <IconChartBar className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-gray-400">Nifty50 Benchmark</span>
          </div>
          <p className="text-2xl font-bold text-gray-300">
            {data.returns.nifty50 >= 0 ? '+' : ''}{data.returns.nifty50.toFixed(2)}%
          </p>
          <p className="text-xs text-gray-400 mt-1">
            ₹{data.final_values.nifty50.toLocaleString('en-IN')}
          </p>
        </div>

        <div className="bg-[#141414] rounded-lg p-4 border border-[rgba(255,255,255,0.07)]">
          <div className="flex items-center gap-2 mb-2">
            <IconArrowUpRight className="w-4 h-4 text-[#a0a0a0]" />
            <span className="text-xs text-gray-400">Outperformance</span>
          </div>
          <p className="text-2xl font-bold text-[#a0a0a0]">
            {data.returns.outperformance_vs_nifty >= 0 ? '+' : ''}
            {data.returns.outperformance_vs_nifty.toFixed(2)}%
          </p>
          <p className="text-xs text-gray-400 mt-1">vs Nifty50</p>
        </div>
      </div>

      {/* Line Chart */}
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={sampledData}>
          <defs>
            <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="predictedGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#c8ff00" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#c8ff00" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="niftyGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6b7280" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#6b7280" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="date"
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
            tickFormatter={(value, index) => {
              // Show every 5th tick
              return index % 5 === 0 ? value : '';
            }}
          />
          <YAxis
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(0, 0, 0, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              padding: '12px'
            }}
            formatter={(value: number, name: string) => {
              const label = {
                actual: 'Actual Portfolio',
                predicted: 'ML Predicted',
                nifty50: 'Nifty50'
              }[name] || name;
              return [`₹${value.toLocaleString('en-IN')}`, label];
            }}
            labelFormatter={(label) => {
              const item = chartData.find(d => d.date === label);
              return item?.fullDate || label;
            }}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#10b981"
            strokeWidth={3}
            dot={false}
            fill="url(#actualGradient)"
            fillOpacity={1}
            name="actual"
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#c8ff00"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="predicted"
          />
          <Line
            type="monotone"
            dataKey="nifty50"
            stroke="#6b7280"
            strokeWidth={2}
            dot={false}
            fill="url(#niftyGradient)"
            fillOpacity={1}
            name="nifty50"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex justify-center gap-6 mt-6 pt-4 border-t border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-green-500"></div>
          <span className="text-sm text-gray-400">Actual Portfolio</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-blue-500 border-dashed"></div>
          <span className="text-sm text-gray-400">ML Predicted</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-gray-500"></div>
          <span className="text-sm text-gray-400">Nifty50 Benchmark</span>
        </div>
      </div>

      {/* Insights */}
      <div className="mt-6 p-4 bg-blue-500/10 rounded-xl border border-blue-500/20">
        <div className="flex items-start gap-3">
          <IconAlertCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-semibold text-blue-400 mb-1">Performance Insights</p>
            <p className="text-sm text-gray-300">
              Your portfolio {data.returns.actual > data.returns.nifty50 ? 'outperformed' : 'underperformed'} the Nifty50 benchmark by{' '}
              <span className={`font-semibold ${data.returns.outperformance_vs_nifty >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {Math.abs(data.returns.outperformance_vs_nifty).toFixed(2)}%
              </span>
              {' '}over the last {data.timeframe_days} days. Our ML model ({data.strategy}) predicted returns with{' '}
              <span className="font-semibold text-blue-400">{data.returns.prediction_accuracy.toFixed(1)}%</span> accuracy.
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

