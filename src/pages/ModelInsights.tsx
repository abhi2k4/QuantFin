import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Brain, Activity, TrendingUp, Loader2, RefreshCw, Zap, CheckCircle, XCircle } from 'lucide-react';
import { getModelPerformance, getTrainingStatus, trainModels, getErrorMessage, type ModelPerformance } from '@/services/api';
import { toast } from 'sonner';

export default function ModelInsights() {
  const [models, setModels] = useState<ModelPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const data = await getModelPerformance(false);
      setModels(data);
    } catch (error) {
      console.error('Error loading models:', error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModels = async () => {
    setTraining(true);
    const toastId = toast.loading('Training models...');

    try {
      await trainModels(true);

      const startedAt = Date.now();
      const timeoutMs = 10 * 60 * 1000; // 10 minutes

      while (true) {
        const status = await getTrainingStatus();

        if (status.status === 'completed') {
          break;
        }
        if (status.status === 'failed') {
          throw new Error(status.error || 'Model training failed');
        }

        if (Date.now() - startedAt > timeoutMs) {
          throw new Error('Model training timed out');
        }

        // Polling interval
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }

      await loadModels();
      toast.success('Models trained successfully!', { id: toastId });
    } catch (error) {
      console.error('Error training models:', error);
      const message = error instanceof Error ? error.message : getErrorMessage(error);
      toast.error(message, { id: toastId });
    } finally {
      setTraining(false);
    }
  };

  const getModelIcon = (model: string) => {
    if (model.includes('LSTM')) return Brain;
    if (model.includes('ARIMA')) return Activity;
    return TrendingUp;
  };

  const getModelColor = (model: string) => {
    const colors: Record<string, string> = {
      'LSTM': 'text-blue-400',
      'Linear Regression': 'text-green-400',
      'SVM': 'text-purple-400',
      'ARIMA': 'text-orange-400'
    };
    return colors[model] || 'text-cyan-400';
  };

  const getBestModel = () => {
    if (models.length === 0) return null;
    return models.reduce((best, current) => 
      current.accuracy > best.accuracy ? current : best
    );
  };

  const bestModel = getBestModel();

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 text-white">
        {/* Top Bar */}
        <div className="sticky top-0 z-50 backdrop-blur-xl bg-zinc-950/80 border-b border-white/5">
          <div className="max-w-[1600px] mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-3">
                  <Brain className="w-6 h-6 text-blue-400" />
                  Model Insights
                </h1>
                <p className="text-sm text-gray-400 mt-1">AI model performance and training status</p>
              </div>
              <div className="flex gap-3">
                <Button
                  onClick={handleTrainModels}
                  disabled={training || loading}
                  className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0"
                >
                  {training ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Training...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      Train Models
                    </>
                  )}
                </Button>
                <Button
                  onClick={() => loadModels()}
                  disabled={loading || training}
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
          {loading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-20"
            >
              <Loader2 className="w-12 h-12 text-blue-400 animate-spin mb-4" />
              <p className="text-gray-400">Loading model performance data...</p>
            </motion.div>
          ) : (
            <>
              {/* Model Cards Grid */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
              >
                {models.map((model, i) => {
                  const Icon = getModelIcon(model.model);
                  const colorClass = getModelColor(model.model);
                  const isBest = bestModel?.model === model.model;
                  
                  return (
                    <motion.div
                      key={model.model}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.1 + 0.2 }}
                    >
                      <Card className={`relative p-6 bg-white/5 backdrop-blur-xl border-white/10 hover:border-white/20 transition-all ${
                        isBest ? 'ring-2 ring-yellow-500/50' : ''
                      }`}>
                        {isBest && (
                          <div className="absolute top-2 right-2">
                            <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded-full font-semibold">
                              Best
                            </span>
                          </div>
                        )}
                        <Icon className={`w-10 h-10 ${colorClass} mb-4`} />
                        <h3 className="font-semibold text-lg mb-2">{model.model}</h3>
                        <p className={`text-3xl font-bold ${colorClass} mb-1`}>
                          {(model.accuracy > 1 ? model.accuracy : model.accuracy * 100).toFixed(1)}%
                        </p>
                        <p className="text-sm text-gray-400 mb-4">Test Accuracy</p>
                        
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between items-center">
                            <span className="text-gray-400">Train Acc:</span>
                            <span className="text-white font-medium">{(model.train_accuracy > 1 ? model.train_accuracy : model.train_accuracy * 100).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-gray-400">R² Score:</span>
                            <span className="text-white font-medium">{model.r2_score.toFixed(3)}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-gray-400">RMSE:</span>
                            <span className="text-white font-medium">{model.rmse.toFixed(2)}</span>
                          </div>
                        </div>

                        {model.status && (
                          <div className="mt-4 pt-4 border-t border-white/10">
                            <div className="flex items-center gap-2">
                              {model.status === 'trained' ? (
                                <>
                                  <CheckCircle className="w-4 h-4 text-green-400" />
                                  <span className="text-xs text-green-400">Trained</span>
                                </>
                              ) : (
                                <>
                                  <XCircle className="w-4 h-4 text-yellow-400" />
                                  <span className="text-xs text-yellow-400">Needs Training</span>
                                </>
                              )}
                            </div>
                          </div>
                        )}
                      </Card>
                    </motion.div>
                  );
                })}
              </motion.div>

              {/* Model Comparison Table */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <Card className="bg-white/5 backdrop-blur-xl border-white/10 p-6">
                  <h3 className="text-lg font-semibold mb-4">Detailed Model Comparison</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-white/10">
                          <th className="text-left py-3 px-4 text-gray-400 font-semibold">Model</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-semibold">Test Accuracy</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-semibold">Train Accuracy</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-semibold">MAE</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-semibold">RMSE</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-semibold">R² Score</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-semibold">Samples</th>
                        </tr>
                      </thead>
                      <tbody>
                        {models.map((model) => {
                          const isBest = bestModel?.model === model.model;
                          return (
                            <tr
                              key={model.model}
                              className={`border-b border-white/5 hover:bg-white/5 transition-colors ${
                                isBest ? 'bg-yellow-500/5' : ''
                              }`}
                            >
                              <td className="py-3 px-4 font-medium">
                                {model.model}
                                {isBest && (
                                  <span className="ml-2 text-xs text-yellow-400">★</span>
                                )}
                              </td>
                              <td className="py-3 px-4 text-right font-mono text-green-400">
                                {(model.accuracy > 1 ? model.accuracy : model.accuracy * 100).toFixed(2)}%
                              </td>
                              <td className="py-3 px-4 text-right font-mono text-blue-400">
                                {(model.train_accuracy > 1 ? model.train_accuracy : model.train_accuracy * 100).toFixed(2)}%
                              </td>
                              <td className="py-3 px-4 text-right font-mono text-gray-400">
                                {model.mae.toFixed(2)}
                              </td>
                              <td className="py-3 px-4 text-right font-mono text-gray-400">
                                {model.rmse.toFixed(2)}
                              </td>
                              <td className="py-3 px-4 text-right font-mono text-purple-400">
                                {model.r2_score.toFixed(3)}
                              </td>
                              <td className="py-3 px-4 text-right text-gray-400">
                                {model.training_samples.toLocaleString()}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </Card>
              </motion.div>

              {/* Training Info */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <Card className="bg-blue-500/10 border-blue-500/20 p-4">
                  <div className="flex items-start gap-3">
                    <Brain className="w-5 h-5 text-blue-400 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="font-semibold text-blue-300 mb-1">Model Training Information</h4>
                      <p className="text-sm text-blue-200/80">
                        All models are trained on historical stock data. Click "Train Models" to retrain with the latest data. 
                        Training typically takes 30-60 seconds. The best performing model is highlighted with a ★ marker.
                      </p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
