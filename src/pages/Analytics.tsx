import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Area
} from 'recharts';
import {
  Brain,
  TrendingUp,
  Activity,
  BarChart3,
  Zap,
  Target,
  Award,
  ArrowUpRight,
  ArrowDownRight,
  Loader2
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { getModelPerformance, getCandlestickData, getBacktestResults, getErrorMessage } from '@/services/api';

type ModelType = 'LSTM' | 'Linear Regression' | 'SVM' | 'ARIMA';

interface ModelMetrics {
  model: string;
  accuracy: number;
  train_accuracy: number;
  rmse: number;
  mae: number;
  r2_score: number;
  training_samples: number;
  status?: string;
}

interface CandlestickData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export default function Analytics() {
  const [models, setModels] = useState<ModelMetrics[]>([]);
  const [candlestickData, setCandlestickData] = useState<CandlestickData[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE');
  const [selectedModel, setSelectedModel] = useState<ModelType>('LSTM');
  const [loading, setLoading] = useState(true);
  const [candlestickLoading, setCandlestickLoading] = useState(false);
  const [trainingModels, setTrainingModels] = useState(false);

  const symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN'];

  useEffect(() => {
    loadModels();
    loadCandlestickData(selectedSymbol);
  }, []);

  const loadModels = async (forceTrain = false) => {
    setLoading(true);
    try {
      const data = await getModelPerformance(forceTrain);
      setModels(data);
    } catch (error) {
      console.error('Error loading models:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const loadCandlestickData = async (symbol: string) => {
    setCandlestickLoading(true);
    try {
      const data = await getCandlestickData(symbol, 90);
      setCandlestickData(data.data);
    } catch (error) {
      console.error('Error loading candlestick data:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setCandlestickLoading(false);
    }
  };

  const handleSymbolChange = (symbol: string) => {
    setSelectedSymbol(symbol);
    loadCandlestickData(symbol);
  };

  const handleTrainModels = () => {
    setTrainingModels(true);
    toast.info('Training models... This may take 30+ seconds');
    loadModels(true).finally(() => setTrainingModels(false));
  };

  const getModelColor = (model: string) => {
    const colors: Record<string, string> = {
      'LSTM': '#3b82f6',
      'Linear Regression': '#10b981',
      'SVM': '#8b5cf6',
      'ARIMA': '#f59e0b'
    };
    return colors[model] || '#6b7280';
  };

  const getBestModel = () => {
    if (models.length === 0) return null;
    return models.reduce((best, current) => 
      current.accuracy > best.accuracy ? current : best
    );
  };

  const bestModel = getBestModel();

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 text-white">
      {/* Top Bar */}
      <div className="sticky top-0 z-50 backdrop-blur-xl bg-zinc-950/80 border-b border-white/5">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-3">
                <Brain className="w-6 h-6 text-blue-400" />
                ML Analytics & Predictions
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                Compare model performance, view predictions, and analyze market trends
              </p>
            </div>
            <Button
              onClick={handleTrainModels}
              disabled={trainingModels}
              className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0"
            >
              {trainingModels ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Training...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Retrain Models
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-6 py-6 space-y-6">
        {/* Model Comparison Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                <div className="animate-pulse space-y-3">
                  <div className="h-4 bg-white/20 rounded w-3/4"></div>
                  <div className="h-8 bg-white/20 rounded w-1/2"></div>
                  <div className="h-3 bg-white/20 rounded w-full"></div>
                </div>
              </Card>
            ))
          ) : (
            models.map((model, index) => {
              const isBest = bestModel?.model === model.model;
              return (
                <motion.div
                  key={model.model}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className={`bg-white/5 backdrop-blur-xl border-white/10 p-6 relative overflow-hidden ${
                    isBest ? 'ring-2 ring-yellow-500/50' : ''
                  }`}>
                    {isBest && (
                      <div className="absolute top-2 right-2">
                        <Award className="w-6 h-6 text-yellow-500" />
                      </div>
                    )}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-white">{model.model}</h3>
                        <div style={{ color: getModelColor(model.model) }}>
                          <Brain className="w-5 h-5" />
                        </div>
                      </div>
                      
                      <div>
                        <div className="text-3xl font-bold text-white">
                          {(model.accuracy * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-400">Test Accuracy</div>
                      </div>

                      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/10">
                        <div>
                          <div className="text-xs text-gray-500">RMSE</div>
                          <div className="text-sm font-semibold text-white">{model.rmse.toFixed(2)}</div>
                        </div>
                        <div>
                          <div className="text-xs text-gray-500">R² Score</div>
                          <div className="text-sm font-semibold text-white">{model.r2_score.toFixed(3)}</div>
                        </div>
                      </div>

                      {model.status === 'cached' && (
                        <div className="text-xs text-blue-400 flex items-center gap-1">
                          <Activity className="w-3 h-3" />
                          Cached metrics
                        </div>
                      )}
                    </div>
                  </Card>
                </motion.div>
              );
            })
          )}
        </motion.div>

        {/* Model Comparison Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-purple-400" />
              Model Performance Comparison
            </h2>
            
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={models.map(m => ({
                ...m,
                accuracy: m.accuracy * 100,
                train_accuracy: m.train_accuracy * 100
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="model" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(17, 24, 39, 0.95)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Bar dataKey="accuracy" name="Test Accuracy (%)" fill="#3b82f6" />
                <Bar dataKey="train_accuracy" name="Train Accuracy (%)" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>

        {/* Candlestick Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-green-400" />
                Price Action - {selectedSymbol}
              </h2>
              
              <div className="flex gap-2">
                {symbols.map(symbol => (
                  <Button
                    key={symbol}
                    onClick={() => handleSymbolChange(symbol)}
                    variant={selectedSymbol === symbol ? 'default' : 'outline'}
                    size="sm"
                    className={selectedSymbol === symbol ? 'bg-blue-600' : ''}
                  >
                    {symbol}
                  </Button>
                ))}
              </div>
            </div>

            {candlestickLoading ? (
              <div className="flex items-center justify-center h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={400}>
                <ComposedChart data={candlestickData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#9ca3af"
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis stroke="#9ca3af" domain={['dataMin - 50', 'dataMax + 50']} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(17, 24, 39, 0.95)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px'
                    }}
                    formatter={(value: number) => [`₹${value.toFixed(2)}`, '']}
                  />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="close" 
                    fill="#3b82f680" 
                    stroke="#3b82f6" 
                    name="Close Price"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="high" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    name="High"
                    dot={false}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="low" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    name="Low"
                    dot={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            )}

            {!candlestickLoading && candlestickData.length > 0 && (
              <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10">
                <div>
                  <div className="text-sm text-gray-400">Latest Close</div>
                  <div className="text-xl font-bold text-white">
                    ₹{candlestickData[candlestickData.length - 1].close.toFixed(2)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">High (90D)</div>
                  <div className="text-xl font-bold text-green-500">
                    ₹{Math.max(...candlestickData.map(d => d.high)).toFixed(2)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Low (90D)</div>
                  <div className="text-xl font-bold text-red-500">
                    ₹{Math.min(...candlestickData.map(d => d.low)).toFixed(2)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Avg Volume</div>
                  <div className="text-xl font-bold text-white">
                    {(candlestickData.reduce((sum, d) => sum + d.volume, 0) / candlestickData.length / 1000000).toFixed(2)}M
                  </div>
                </div>
              </div>
            )}
          </Card>
        </motion.div>

        {/* Metrics Comparison Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <Target className="w-6 h-6 text-orange-400" />
              Detailed Metrics Comparison
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Model</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Train Acc</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Test Acc</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">RMSE</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">MAE</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">R²</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Samples</th>
                  </tr>
                </thead>
                <tbody>
                  {models.map((model, index) => (
                    <motion.tr
                      key={model.model}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      <td className="py-3 px-4 font-medium text-white">{model.model}</td>
                      <td className="py-3 px-4 text-right text-green-400">
                        {(model.train_accuracy * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 px-4 text-right font-semibold text-blue-400">
                        {(model.accuracy * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 px-4 text-right text-gray-300">
                        {model.rmse.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-300">
                        {model.mae.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-right text-purple-400">
                        {model.r2_score.toFixed(3)}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-400">
                        {model.training_samples.toLocaleString()}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
