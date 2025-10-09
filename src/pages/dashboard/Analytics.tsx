import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  BarChart3,
  Loader2,
  ChevronDown,
  Sparkles,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import {
  getAnalyticsKPIs,
  getModelPerformance,
  getStockPrediction,
  getRecommendations,
  getErrorMessage,
  type KPIData,
  type ModelPerformance,
  type StockPrediction,
  type Recommendation
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
  const [stockData, setStockData] = useState<StockPrediction | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  // Loading states
  const [loadingKPIs, setLoadingKPIs] = useState(true);
  const [loadingModels, setLoadingModels] = useState(true);
  const [loadingStock, setLoadingStock] = useState(true);
  const [loadingRecs, setLoadingRecs] = useState(true);

  // Fetch data on mount and when filters change
  useEffect(() => {
    loadKPIs();
    loadModelPerformance();
    loadRecommendations();
  }, [timeframe]);

  useEffect(() => {
    loadStockPrediction();
  }, [selectedStock, timeframe]);

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

  const loadStockPrediction = async () => {
    setLoadingStock(true);
    try {
      const data = await getStockPrediction(selectedStock, timeframe);
      setStockData(data);
    } catch (error) {
      console.error('Error loading stock prediction:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoadingStock(false);
    }
  };

  const loadRecommendations = async () => {
    setLoadingRecs(true);
    try {
      const data = await getRecommendations();
      setRecommendations(data);
    } catch (error) {
      console.error('Error loading recommendations:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoadingRecs(false);
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
                <BarChart3 className="w-5 h-5" />
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
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
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
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
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
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
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

        {/* Stock Prediction vs Actual */}
        <StockPredictionSection
          data={stockData}
          selectedModel={selectedModel}
          loading={loadingStock}
        />

        {/* Recommendations */}
        <RecommendationsSection
          data={recommendations}
          loading={loadingRecs}
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
      icon: TrendingUp,
      color: 'from-green-500 to-emerald-600',
      bgColor: 'bg-green-500/10',
      trend: 'up'
    },
    {
      title: 'Risk Metric',
      value: kpis?.risk_metric,
      suffix: '',
      icon: ShieldCheck,
      color: 'from-blue-500 to-cyan-600',
      bgColor: 'bg-blue-500/10',
      trend: 'neutral'
    },
    {
      title: 'Volatility',
      value: kpis?.volatility,
      suffix: '%',
      icon: Activity,
      color: 'from-orange-500 to-amber-600',
      bgColor: 'bg-orange-500/10',
      trend: 'neutral'
    },
    {
      title: 'Sharpe Ratio',
      value: kpis?.sharpe_ratio,
      suffix: '',
      icon: Target,
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
                <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
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
                <TrendingUp className="w-4 h-4" />
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
          <Sparkles className="w-5 h-5" />
        </div>
      </div>

      {loading ? (
        <div className="h-[400px] flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
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
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Return</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">MAE</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">RMSE</th>
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
                  <td className="py-3 px-4 text-right text-green-500">{model.return}%</td>
                  <td className="py-3 px-4 text-right text-gray-400">{model.mae}</td>
                  <td className="py-3 px-4 text-right text-gray-400">{model.rmse}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
}

// ==================== STOCK PREDICTION SECTION ====================

interface StockPredictionSectionProps {
  data: StockPrediction | null;
  selectedModel: ModelType;
  loading: boolean;
}

function StockPredictionSection({ data, selectedModel, loading }: StockPredictionSectionProps) {
  // Prepare chart data
  const chartData = data
    ? data.dates.map((date, index) => ({
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        actual: data.actual_prices[index],
        predicted:
          selectedModel === 'All'
            ? null
            : data.predicted_prices[selectedModel as keyof typeof data.predicted_prices]?.[index],
        LSTM: selectedModel === 'All' ? data.predicted_prices.LSTM[index] : null,
        Linear: selectedModel === 'All' ? data.predicted_prices.Linear[index] : null,
        Logistic: selectedModel === 'All' ? data.predicted_prices.Logistic[index] : null,
        SVM: selectedModel === 'All' ? data.predicted_prices.SVM[index] : null
      }))
    : [];

  // Sample every nth data point for better visualization (show ~30 points max)
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
          <h2 className="text-xl font-bold">Stock Predictions vs Actual</h2>
          <p className="text-sm text-gray-400 mt-1">
            {data?.symbol} • {selectedModel === 'All' ? 'All Models' : `${selectedModel} Model`}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="h-[400px] flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : (
        <AnimatePresence mode="wait">
          <motion.div
            key={selectedModel}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={sampledData}>
                <defs>
                  <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="predictedGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis
                  dataKey="date"
                  stroke="#666"
                  tick={{ fill: '#999', fontSize: 12 }}
                />
                <YAxis stroke="#666" tick={{ fill: '#999' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.95)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px',
                    backdropFilter: 'blur(20px)'
                  }}
                  labelStyle={{ color: '#fff', marginBottom: '8px' }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />

                {/* Actual Price */}
                <Area
                  type="monotone"
                  dataKey="actual"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#actualGradient)"
                  name="Actual Price"
                />

                {/* Predicted Price(s) */}
                {selectedModel !== 'All' && (
                  <Area
                    type="monotone"
                    dataKey="predicted"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    fill="url(#predictedGradient)"
                    strokeDasharray="5 5"
                    name={`${selectedModel} Prediction`}
                  />
                )}

                {selectedModel === 'All' && (
                  <>
                    <Line type="monotone" dataKey="LSTM" stroke="#8b5cf6" strokeWidth={2} dot={false} name="LSTM" />
                    <Line type="monotone" dataKey="Linear" stroke="#10b981" strokeWidth={2} dot={false} name="Linear" />
                    <Line type="monotone" dataKey="Logistic" stroke="#f59e0b" strokeWidth={2} dot={false} name="Logistic" />
                    <Line type="monotone" dataKey="SVM" stroke="#ef4444" strokeWidth={2} dot={false} name="SVM" />
                  </>
                )}
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>
        </AnimatePresence>
      )}
    </motion.div>
  );
}

// ==================== RECOMMENDATIONS SECTION ====================

interface RecommendationsSectionProps {
  data: Recommendation[];
  loading: boolean;
}

function RecommendationsSection({ data, loading }: RecommendationsSectionProps) {
  const getActionColor = (action: string) => {
    switch (action) {
      case 'Buy':
        return 'from-green-500 to-emerald-600';
      case 'Hold':
        return 'from-blue-500 to-cyan-600';
      case 'Sell':
        return 'from-red-500 to-orange-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'Buy':
        return <TrendingUp className="w-5 h-5" />;
      case 'Hold':
        return <ShieldCheck className="w-5 h-5" />;
      case 'Sell':
        return <TrendingDown className="w-5 h-5" />;
      default:
        return <AlertCircle className="w-5 h-5" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Model Recommendations</h2>
          <p className="text-sm text-gray-400 mt-1">AI-driven trading suggestions based on model performance</p>
        </div>
      </div>

      {loading ? (
        <div className="h-[200px] flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.map((rec, index) => (
            <motion.div
              key={rec.model}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="rounded-xl bg-white/5 border border-white/10 p-5 hover:border-white/20 transition-all hover:shadow-lg"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${getActionColor(rec.action)} flex items-center justify-center`}>
                    {getActionIcon(rec.action)}
                  </div>
                  <div>
                    <h3 className="font-semibold">{rec.model}</h3>
                    <p className="text-xs text-gray-400">ML Model</p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${getActionColor(rec.action)}`}>
                  {rec.action}
                </div>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div>
                  <p className="text-xs text-gray-400">Return</p>
                  <p className="text-lg font-bold text-green-500">{rec.return}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Confidence</p>
                  <p className="text-lg font-bold">{(rec.confidence * 100).toFixed(0)}%</p>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-gray-400 leading-relaxed">{rec.description}</p>

              {/* Confidence Bar */}
              <div className="mt-4 h-2 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${rec.confidence * 100}%` }}
                  transition={{ delay: index * 0.1 + 0.3, duration: 0.8 }}
                  className={`h-full bg-gradient-to-r ${getActionColor(rec.action)}`}
                />
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
