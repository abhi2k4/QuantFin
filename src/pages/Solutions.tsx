import { motion } from 'framer-motion';
import { IconArrowLeft, IconTrendingUp, IconBrain, IconTarget, IconChartBar, IconBolt, IconShield, IconCircleCheck, IconArrowRight } from '@tabler/icons-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15
    }
  }
};

export default function Solutions() {
  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-6 py-24">
        <Link to="/">
          <Button className="btn-secondary mb-8 rounded-xl">
            <IconArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </Link>
        
        <motion.div
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          <motion.h1 variants={fadeInUp} className="text-5xl md:text-6xl font-bold gradient-text mb-6">
            How QuantFin AI Works
          </motion.h1>
          <motion.p variants={fadeInUp} className="text-xl text-gray-400 max-w-3xl mb-16">
            Your intelligent companion for portfolio management. Here's how we transform your investment strategy with AI.
          </motion.p>

          {/* Step-by-Step Flow */}
          <motion.div variants={staggerContainer} className="space-y-12 mb-16">
            {[
              {
                step: '01',
                icon: IconTarget,
                title: 'Connect Your Portfolio',
                desc: 'Simply connect your portfolio or upload historical trading data from the Indian stock market. Our system securely analyzes your Nifty 50 holdings and trading patterns.',
                features: ['Secure data import', 'Nifty 50 stock support', 'Historical data analysis', 'Real-time market sync']
              },
              {
                step: '02',
                icon: IconBrain,
                title: 'AI Analysis & Prediction',
                desc: 'Our ensemble of 4 ML models (LSTM Neural Network, Linear Regression, Logistic Regression, and SVM) process technical indicators including RSI, MACD, and Bollinger Bands to predict market movements.',
                features: ['4 ML models in ensemble', 'Real-time predictions', 'Technical indicator analysis', 'Pattern recognition with TensorFlow']
              },
              {
                step: '03',
                icon: IconChartBar,
                title: 'Portfolio Optimization',
                desc: 'Get AI-powered recommendations for optimal asset allocation. Our algorithms balance risk and return using Modern Portfolio Theory and risk-adjusted metrics.',
                features: ['Sharpe ratio optimization', 'Risk-return analysis', 'Automated rebalancing', 'Diversification insights']
              },
              {
                step: '04',
                icon: IconBolt,
                title: 'Execute & Monitor',
                desc: 'View actionable insights on your dashboard with real-time updates. Track performance, monitor risk metrics, and receive alerts for portfolio rebalancing opportunities.',
                features: ['Live dashboard', 'Performance tracking', 'Risk alerts', 'Backtesting results']
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                variants={fadeInUp}
                className="card relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 text-9xl font-bold text-white/5 leading-none p-8">
                  {item.step}
                </div>
                <div className="relative z-10 grid md:grid-cols-[auto,1fr] gap-6 items-start">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/10">
                    <item.icon className="w-10 h-10 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-3xl font-bold text-white mb-3">{item.title}</h3>
                    <p className="text-gray-400 text-lg mb-6 leading-relaxed">{item.desc}</p>
                    <div className="grid sm:grid-cols-2 gap-3">
                      {item.features.map((feature, j) => (
                        <div key={j} className="flex items-center gap-2">
                          <IconCircleCheck className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                          <span className="text-gray-300 text-sm">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Key Benefits */}
          <motion.div variants={fadeInUp} className="card-flat bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-blue-500/20">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">Why Choose QuantFin AI?</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                { icon: IconShield, title: 'Risk Management', desc: 'Comprehensive risk metrics including volatility, max drawdown, and Value at Risk (VaR)' },
                { icon: IconTrendingUp, title: 'Proven Results', desc: 'Backtested strategies on historical data with transparent performance metrics' },
                { icon: IconBolt, title: 'Real-time Updates', desc: 'Live market data integration with instant portfolio recalculations' }
              ].map((benefit, i) => (
                <div key={i} className="text-center">
                  <benefit.icon className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-white mb-2">{benefit.title}</h3>
                  <p className="text-gray-400 text-sm">{benefit.desc}</p>
                </div>
              ))}
            </div>
          </motion.div>

          {/* CTA */}
          <motion.div variants={fadeInUp} className="text-center mt-16">
            <Link to="/dashboard">
              <Button className="btn-primary text-lg px-10 py-4 h-auto rounded-xl group">
                Try QuantFin Now
                <IconArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <p className="text-gray-500 text-sm mt-4">No credit card required • Free demo access</p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
