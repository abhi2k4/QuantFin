import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { IconTrendingUp, IconActivity, IconTarget, IconChartBar, IconLoader, IconChevronDown, IconSparkles, IconShieldCheck } from '@tabler/icons-react';
import {
  getAnalyticsKPIs,
  getModelPerformance,
  getErrorMessage,
  type KPIData,
  type ModelPerformance
} from '@/services/api';
import { toast } from 'sonner';

// ==================== TYPE DEFINITIONS ====================

type Timeframe = '1M' | '3M' | '6M' | '1Y';
type ModelType = 'LSTM' | 'Linear' | 'Logistic' | 'SVM' | 'All';

// ==================== MAIN COMPONENT ====================

export default function Analytics() {
  // State management
  const [timeframe, setTimeframe] = useState<Timeframe>('3M');
  const [selectedModel, setSelectedModel] = useState<ModelType>('LSTM');
  const [selectedStock, setSelectedStock] = useState('RELIANCE');

  // Data state
  const [kpis, setKpis] = useState<KPIData | null>(null);
  const [modelPerf, setModelPerf] = useState<ModelPerformance[]>([]);

  // Loading states
  const [loadingKPIs, setLoadingKPIs] = useState(true);
  const [loadingModels, setLoadingModels] = useState(true);

  // Fetch data on mount and when filters change
  useEffect(() => {
    loadKPIs();
    loadModelPerformance();
  }, [timeframe]);

  const loadKPIs = async () => {
    setLoadingKPIs(true);
    try {
      const data = await getAnalyticsKPIs();
      setKpis(data);
    } catch (error) {
      console.error('Error loading KPIs:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoadingKPIs(false);
    }
  };

  const loadModelPerformance = async () => {
    setLoadingModels(true);
    try {
      const data = await getModelPerformance();
      setModelPerf(data);
    } catch (error) {
      console.error('Error loading model performance:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoadingModels(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 text-white">
      {/* Top Bar */}
      <div className="sticky top-0 z-50 backdrop-blur-xl bg-zinc-950/80 border-b border-white/5">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <IconChartBar className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
                <p className="text-sm text-gray-400">ML Model Performance & Predictions</p>
              </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-3">
              {/* Timeframe Selector */}
              <div className="relative">
                <select
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value as Timeframe)}
                  className="appearance-none pl-4 pr-10 py-2.5 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                >
                  <option value="1M">1 Month</option>
                  <option value="3M">3 Months</option>
                  <option value="6M">6 Months</option>
                  <option value="1Y">1 Year</option>
                </select>
                <IconChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>

              {/* Stock Selector */}
              <div className="relative">
                <select
                  value={selectedStock}
                  onChange={(e) => setSelectedStock(e.target.value)}
                  className="appearance-none pl-4 pr-10 py-2.5 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                >
                  <option value="RELIANCE">RELIANCE</option>
                  <option value="TCS">TCS</option>
                  <option value="HDFCBANK">HDFCBANK</option>
                  <option value="INFY">INFY</option>
                </select>
                <IconChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>

              {/* Model Filter */}
              <div className="relative">
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value as ModelType)}
                  className="appearance-none pl-4 pr-10 py-2.5 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                >
                  <option value="LSTM">LSTM Model</option>
                  <option value="Linear">Linear Regression</option>
                  <option value="Logistic">Logistic Regression</option>
                  <option value="SVM">SVM Model</option>
                  <option value="All">All Models</option>
                </select>
                <IconChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-6 py-8 space-y-8">
        {/* KPI Cards */}
        <KPICards kpis={kpis} loading={loadingKPIs} />

        {/* ML Model Performance Charts */}
        <ModelPerformanceSection
          data={modelPerf}
          loading={loadingModels}
        />
      </div>
    </div>
  );
}

// ==================== KPI CARDS COMPONENT ====================

interface KPICardsProps {
  kpis: KPIData | null;
  loading: boolean;
}

function KPICards({ kpis, loading }: KPICardsProps) {
  const kpiConfig = [
    {
      title: 'Portfolio Return',
      value: kpis?.portfolio_return,
      suffix: '%',
      icon: IconTrendingUp,
      color: 'from-green-500 to-emerald-600',
      bgColor: 'bg-green-500/10',
      trend: 'up'
    },
    {
      title: 'Risk Metric',
      value: kpis?.risk_metric,
      suffix: '',
      icon: IconShieldCheck,
      color: 'from-blue-500 to-cyan-600',
      bgColor: 'bg-blue-500/10',
      trend: 'neutral'
    },
    {
      title: 'Volatility',
      value: kpis?.volatility,
      suffix: '%',
      icon: IconActivity,
      color: 'from-orange-500 to-amber-600',
      bgColor: 'bg-orange-500/10',
      trend: 'neutral'
    },
    {
      title: 'Sharpe Ratio',
      value: kpis?.sharpe_ratio,
      suffix: '',
      icon: IconTarget,
      color: 'from-purple-500 to-pink-600',
      bgColor: 'bg-purple-500/10',
      trend: 'up'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {kpiConfig.map((kpi, index) => (
        <motion.div
          key={kpi.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="relative group"
        >
          <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6 hover:border-white/20 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10">
            {/* Icon */}
            <div className={`w-12 h-12 rounded-xl ${kpi.bgColor} flex items-center justify-center mb-4`}>
              <kpi.icon className={`w-6 h-6 bg-gradient-to-br ${kpi.color} bg-clip-text text-transparent`} style={{ WebkitTextFillColor: 'transparent', WebkitBackgroundClip: 'text', backgroundClip: 'text' }} />
            </div>

            {/* Title */}
            <p className="text-sm text-gray-400 mb-2">{kpi.title}</p>

            {/* Value */}
            {loading ? (
              <div className="flex items-center gap-2">
                <IconLoader className="w-5 h-5 animate-spin text-blue-500" />
                <span className="text-gray-500">Loading...</span>
              </div>
            ) : (
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: index * 0.1 + 0.2, type: 'spring' }}
                className="flex items-baseline gap-1"
              >
                <span className="text-3xl font-bold">{kpi.value?.toFixed(2)}</span>
                <span className="text-lg text-gray-400">{kpi.suffix}</span>
              </motion.div>
            )}

            {/* Trend indicator */}
            {!loading && kpi.trend === 'up' && (
              <div className="mt-3 flex items-center gap-1 text-green-500 text-sm">
                <IconTrendingUp className="w-4 h-4" />
                <span>Positive</span>
              </div>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}

// ==================== MODEL PERFORMANCE SECTION ====================

interface ModelPerformanceSectionProps {
  data: ModelPerformance[];
  loading: boolean;
}

function ModelPerformanceSection({ data, loading }: ModelPerformanceSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">ML Model Performance</h2>
          <p className="text-sm text-gray-400 mt-1">Accuracy and returns comparison across all models</p>
        </div>
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
          <IconSparkles className="w-5 h-5" />
        </div>
      </div>

      {loading ? (
        <div className="h-[400px] flex items-center justify-center">
          <IconLoader className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Accuracy Chart */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-4">Model Accuracy (%)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis
                  dataKey="model"
                  stroke="#666"
                  tick={{ fill: '#999' }}
                />
                <YAxis stroke="#666" tick={{ fill: '#999' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px',
                    backdropFilter: 'blur(20px)'
                  }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar
                  dataKey="accuracy"
                  fill="url(#accuracyGradient)"
                  radius={[8, 8, 0, 0]}
                />
                <defs>
                  <linearGradient id="accuracyGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#8b5cf6" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Returns Chart */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-4">Portfolio Return (%)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis
                  dataKey="model"
                  stroke="#666"
                  tick={{ fill: '#999' }}
                />
                <YAxis stroke="#666" tick={{ fill: '#999' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px'
                  }}
                />
                <Bar
                  dataKey="return"
                  fill="url(#returnGradient)"
                  radius={[8, 8, 0, 0]}
                />
                <defs>
                  <linearGradient id="returnGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" />
                    <stop offset="100%" stopColor="#059669" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Model Metrics Table */}
      {!loading && (
        <div className="mt-6 overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Model</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Accuracy</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">MAE</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">RMSE</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">R² Score</th>
              </tr>
            </thead>
            <tbody>
              {data.map((model, index) => (
                <motion.tr
                  key={model.model}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors"
                >
                  <td className="py-3 px-4 font-medium">{model.model}</td>
                  <td className="py-3 px-4 text-right">{model.accuracy}%</td>
                  <td className="py-3 px-4 text-right text-gray-400">{model.mae}</td>
                  <td className="py-3 px-4 text-right text-gray-400">{model.rmse}</td>
                  <td className="py-3 px-4 text-right text-gray-400">{model.r2_score}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
}
