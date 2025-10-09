import { motion } from 'framer-motion';
import { TrendingUp, Bot, Shield, Zap, ArrowRight, BarChart3, Brain, Target, Users, Briefcase, UserCheck, Github, Twitter, Linkedin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
};

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Gradient Orbs */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"></div>
        
        <div className="container mx-auto px-6 pt-32 pb-24 relative z-10">
          <motion.div
            className="text-center max-w-5xl mx-auto"
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp} className="mb-6">
              <span className="text-5xl mb-4 inline-block">📊</span>
            </motion.div>
            
            <motion.h1
              variants={fadeInUp}
              className="text-6xl md:text-8xl font-bold mb-6 leading-tight"
            >
              <span className="gradient-text">QuantFin AI</span>
              <br />
              <span className="text-4xl md:text-6xl text-gray-300 font-normal">
                Intelligent Portfolio Management
              </span>
            </motion.h1>
            
            <motion.p
              variants={fadeInUp}
              className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed"
            >
              AI-powered ETF portfolio management for the Indian stock market. 
              Optimize portfolios, predict trends, and maximize returns with confidence.
            </motion.p>
            
            <motion.div
              variants={fadeInUp}
              className="flex gap-4 justify-center flex-wrap"
            >
              <Link to="/dashboard">
                <Button className="btn-primary text-base px-8 py-3.5 h-auto rounded-xl group">
                  Try QuantFin
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link to="/signup">
                <Button className="btn-secondary text-base px-8 py-3.5 h-auto rounded-xl">
                  Get Started Free
                </Button>
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* About Section */}
      <section className="section-padding bg-gradient-to-b from-transparent to-white/5">
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center mb-16"
          >
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Smarter Decisions, Powered by AI
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-xl text-gray-400 max-w-3xl mx-auto">
              QuantFin AI leverages advanced machine learning algorithms to empower investors 
              with smarter, data-driven decisions.
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {[
              {
                icon: Bot,
                title: 'ML Predictions',
                emoji: '🤖',
                desc: 'Ensemble of 4 models (LSTM, Linear/Logistic Regression, SVM) trained on Nifty 50 stocks',
                gradient: 'from-blue-500/20 to-cyan-500/20',
                iconColor: 'text-blue-400'
              },
              {
                icon: BarChart3,
                title: 'Portfolio Optimization',
                emoji: '📈',
                desc: 'Risk-adjusted allocation strategies with automated rebalancing and comprehensive backtesting',
                gradient: 'from-emerald-500/20 to-teal-500/20',
                iconColor: 'text-emerald-400'
              },
              {
                icon: Shield,
                title: 'Risk Management',
                emoji: '🛡️',
                desc: 'Sharpe ratio, maximum drawdown, volatility analysis with real-time risk metrics',
                gradient: 'from-purple-500/20 to-pink-500/20',
                iconColor: 'text-purple-400'
              },
              {
                icon: Zap,
                title: 'Real-time Insights',
                emoji: '⚡',
                desc: 'Live yfinance data integration with technical indicators (RSI, MACD, Bollinger Bands)',
                gradient: 'from-yellow-500/20 to-orange-500/20',
                iconColor: 'text-yellow-400'
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                variants={fadeInUp}
                className="card group relative overflow-hidden"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
                <div className="relative z-10">
                  <div className="text-4xl mb-4">{feature.emoji}</div>
                  <h3 className="text-xl font-bold mb-3 text-white">{feature.title}</h3>
                  <p className="text-gray-400 leading-relaxed text-sm">{feature.desc}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="section-padding">
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center mb-16"
          >
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-bold mb-6 text-white">
              How It Works
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-xl text-gray-400">
              Three simple steps to optimize your portfolio
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto"
          >
            {[
              { step: '01', title: 'Connect', desc: 'Link your portfolio or upload historical data', icon: Target, color: 'text-blue-400' },
              { step: '02', title: 'Analyze', desc: 'AI models process data and identify patterns', icon: Brain, color: 'text-purple-400' },
              { step: '03', title: 'Optimize', desc: 'Get actionable insights and recommendations', icon: TrendingUp, color: 'text-emerald-400' }
            ].map((item, i) => (
              <motion.div
                key={i}
                variants={fadeInUp}
                className="relative"
              >
                <div className="stat-card text-center relative overflow-hidden group">
                  <div className="absolute top-0 right-0 text-8xl font-bold text-white/5">{item.step}</div>
                  <div className="relative z-10">
                    <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white/5 border border-white/10 mb-6 ${item.color}`}>
                      <item.icon className="w-8 h-8" />
                    </div>
                    <h3 className="text-2xl font-bold mb-3 text-white">{item.title}</h3>
                    <p className="text-gray-400">{item.desc}</p>
                  </div>
                </div>
                {i < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-white/20 to-transparent"></div>
                )}
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="section-padding bg-gradient-to-b from-transparent to-white/5">
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center mb-16"
          >
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Powered by Cutting-Edge Technology
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-xl text-gray-400">
              Built with industry-leading tools and frameworks
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto"
          >
            {[
              { title: 'Backend', tech: ['FastAPI', 'Python 3.11', 'TensorFlow', 'scikit-learn', 'yfinance'] },
              { title: 'Frontend', tech: ['React 18', 'TypeScript', 'Vite', 'Tailwind CSS', 'Framer Motion'] },
              { title: 'ML Models', tech: ['LSTM Neural Network', 'Linear Regression', 'Logistic Regression', 'SVM'] }
            ].map((stack, i) => (
              <motion.div
                key={i}
                variants={fadeInUp}
                className="card-flat"
              >
                <h3 className="text-xl font-bold mb-4 text-white">{stack.title}</h3>
                <div className="flex flex-wrap gap-2">
                  {stack.tech.map((item, j) => (
                    <span
                      key={j}
                      className="badge badge-info"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Target Users Section */}
      <section className="section-padding">
        <div className="container mx-auto px-6">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="text-center mb-16"
          >
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Built for Professionals
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-xl text-gray-400">
              Trusted by investors and advisors across India
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto"
          >
            {[
              { icon: Users, title: 'Retail Investors', desc: 'Make informed decisions with AI-powered insights and predictions' },
              { icon: Briefcase, title: 'Portfolio Managers', desc: 'Optimize client portfolios with advanced risk-adjusted strategies' },
              { icon: UserCheck, title: 'Financial Advisors', desc: 'Provide data-driven recommendations backed by ML models' }
            ].map((user, i) => (
              <motion.div
                key={i}
                variants={fadeInUp}
                className="card text-center group"
              >
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/10 mb-6 group-hover:scale-110 transition-transform">
                  <user.icon className="w-10 h-10 text-blue-400" />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-white">{user.title}</h3>
                <p className="text-gray-400">{user.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
          className="relative overflow-hidden bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-blue-500/10 border-y border-white/10"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/5 to-transparent"></div>
          <div className="container mx-auto px-6 py-20 relative z-10 text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Ready to Transform Your Portfolio?
            </h2>
            <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
              Join thousands of investors leveraging AI for smarter investment decisions
            </p>
            <Link to="/signup">
              <Button className="btn-primary text-base px-8 py-3.5 h-auto rounded-xl">
                Get Started Free
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 bg-black/40 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-12">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-6 h-6 text-blue-400" />
                <span className="text-xl font-bold gradient-text">QuantFin AI</span>
              </div>
              <p className="text-gray-400 text-sm">
                AI-powered portfolio management for the Indian stock market
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white">Company</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
                <li><a href="#careers" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#blog" className="hover:text-white transition-colors">Blog</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white">Legal</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
                <li><Link to="/disclaimer" className="hover:text-white transition-colors">Disclaimer</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4 text-white">Connect</h4>
              <div className="flex gap-3">
                {[
                  { icon: Twitter, href: 'https://twitter.com/quantfin_ai' },
                  { icon: Linkedin, href: 'https://linkedin.com/company/quantfin-ai' },
                  { icon: Github, href: 'https://github.com/abhi2k4/QuantFin' }
                ].map((social, i) => (
                  <a
                    key={i}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center hover:bg-blue-500/20 hover:border-blue-500/50 transition-all"
                  >
                    <social.icon className="w-5 h-5 text-gray-400 hover:text-blue-400" />
                  </a>
                ))}
              </div>
            </div>
          </div>
          
          <div className="border-t border-white/5 pt-8 text-center text-gray-400 text-sm">
            <p>© 2025 QuantFin AI. All rights reserved. Built with ❤️ for investors.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
