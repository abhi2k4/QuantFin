import { motion } from 'framer-motion';
import { IconArrowLeft, IconCode, IconDatabase, IconCpu, IconLayersLinked, IconBolt, IconShield, IconGitBranch, IconArrowRight } from '@tabler/icons-react';
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

export default function Technology() {
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
            Our Technology Stack
          </motion.h1>
          <motion.p variants={fadeInUp} className="text-xl text-gray-400 max-w-3xl mb-16">
            Built with cutting-edge technologies to deliver fast, reliable, and intelligent portfolio management.
          </motion.p>

          {/* Tech Stack Grid */}
          <motion.div variants={staggerContainer} className="grid md:grid-cols-2 gap-8 mb-16">
            {/* Backend */}
            <motion.div variants={fadeInUp} className="card">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center">
                  <IconDatabase className="w-6 h-6 text-blue-400" />
                </div>
                <h2 className="text-2xl font-bold text-white">Backend Infrastructure</h2>
              </div>
              <p className="text-gray-400 mb-6">High-performance API built for real-time data processing and ML model serving.</p>
              <div className="space-y-4">
                {[
                  { name: 'FastAPI', desc: 'Modern Python web framework with async support for lightning-fast API responses' },
                  { name: 'Python 3.11', desc: 'Latest Python version optimized for data science and ML workloads' },
                  { name: 'SQLAlchemy', desc: 'SQL toolkit and ORM for efficient database operations' },
                  { name: 'yfinance', desc: 'Real-time market data from Yahoo Finance for Nifty 50 stocks' }
                ].map((tech, i) => (
                  <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <h3 className="font-semibold text-white mb-1">{tech.name}</h3>
                    <p className="text-sm text-gray-400">{tech.desc}</p>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Frontend */}
            <motion.div variants={fadeInUp} className="card">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                  <IconCode className="w-6 h-6 text-purple-400" />
                </div>
                <h2 className="text-2xl font-bold text-white">Frontend Experience</h2>
              </div>
              <p className="text-gray-400 mb-6">Modern, responsive UI designed for seamless portfolio management.</p>
              <div className="space-y-4">
                {[
                  { name: 'React 18.3', desc: 'Latest React with concurrent rendering for smooth, responsive interfaces' },
                  { name: 'TypeScript', desc: 'Type-safe development for fewer bugs and better developer experience' },
                  { name: 'Vite 5.4', desc: 'Next-gen build tool with instant HMR for rapid development' },
                  { name: 'Tailwind CSS', desc: 'Utility-first CSS framework for beautiful, consistent designs' },
                  { name: 'Framer Motion', desc: 'Production-ready animations and transitions' },
                  { name: 'Recharts & Plotly', desc: 'Interactive data visualization libraries for portfolio charts' }
                ].map((tech, i) => (
                  <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <h3 className="font-semibold text-white mb-1">{tech.name}</h3>
                    <p className="text-sm text-gray-400">{tech.desc}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>

          {/* ML Models Section */}
          <motion.div variants={fadeInUp} className="card mb-16 bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border-emerald-500/20">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center">
                <IconCpu className="w-7 h-7 text-emerald-400" />
              </div>
              <h2 className="text-3xl font-bold text-white">Machine Learning Models</h2>
            </div>
            <p className="text-gray-400 mb-8 text-lg">
              Ensemble of 4 production-ready ML models for accurate stock predictions.
            </p>
            <div className="grid sm:grid-cols-2 gap-4">
              {[
                { name: 'LSTM Neural Network', desc: 'Deep learning with TensorFlow/Keras for sequential time-series forecasting', color: 'emerald' },
                { name: 'Linear Regression', desc: 'Statistical modeling for price trend analysis and relationship identification', color: 'blue' },
                { name: 'Logistic Regression', desc: 'Binary classification for up/down price movement prediction', color: 'cyan' },
                { name: 'SVM (Support Vector Machine)', desc: 'Advanced classification with calibrated probability estimates', color: 'purple' }
              ].map((model, i) => (
                <div key={i} className="p-4 bg-black/20 rounded-xl border border-white/10 hover:border-emerald-500/30 transition-all">
                  <div className="flex items-center gap-2 mb-2">
                    <div className={`w-2 h-2 rounded-full bg-${model.color}-400`}></div>
                    <h3 className="font-bold text-white">{model.name}</h3>
                  </div>
                  <p className="text-sm text-gray-400">{model.desc}</p>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Features Grid */}
          <motion.div variants={staggerContainer} className="grid md:grid-cols-3 gap-6 mb-16">
            {[
              { icon: IconBolt, title: 'Real-time Processing', desc: '73 engineered features calculated in milliseconds for instant insights' },
              { icon: IconShield, title: 'Secure & Reliable', desc: 'Enterprise-grade security with encrypted data storage and transmission' },
              { icon: IconGitBranch, title: 'CI/CD Pipeline', desc: 'Automated testing and deployment for continuous improvements' }
            ].map((feature, i) => (
              <motion.div key={i} variants={fadeInUp} className="stat-card text-center">
                <feature.icon className="w-10 h-10 text-blue-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-gray-400 text-sm">{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* Tech Highlights */}
          <motion.div variants={fadeInUp} className="card-flat">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Technical Highlights</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { title: 'Data Pipeline', points: ['Real-time yfinance data integration', 'Historical Nifty 50 data from 2010-2024', 'Web scraping with BeautifulSoup', 'News sentiment analysis with NLTK'] },
                { title: 'Model Training', points: ['Ensemble of 4 ML models', 'TensorFlow LSTM architecture', 'Walk-forward validation', 'Hyperparameter optimization with GridSearch'] },
                { title: 'Performance', points: ['Async FastAPI endpoints', 'SQLAlchemy ORM optimization', 'Efficient data preprocessing', 'Responsive React frontend'] },
                { title: 'Analytics', points: ['Sharpe ratio calculation', 'Maximum drawdown analysis', 'Volatility forecasting', 'Technical indicators (RSI, MACD, Bollinger Bands)'] }
              ].map((section, i) => (
                <div key={i} className="p-5 bg-white/5 rounded-xl">
                  <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                    <IconLayersLinked className="w-5 h-5 text-blue-400" />
                    {section.title}
                  </h3>
                  <ul className="space-y-2">
                    {section.points.map((point, j) => (
                      <li key={j} className="text-sm text-gray-400 flex items-start gap-2">
                        <span className="text-blue-400 mt-1">•</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </motion.div>

          {/* CTA */}
          <motion.div variants={fadeInUp} className="text-center mt-16">
            <Link to="/dashboard">
              <Button className="btn-primary text-lg px-10 py-4 h-auto rounded-xl group">
                See It In Action
                <IconArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <p className="text-gray-500 text-sm mt-4">Explore our demo dashboard with real data</p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
