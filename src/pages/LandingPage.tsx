import { motion } from 'framer-motion';
import { IconTrendingUp, IconRobot, IconShield, IconBolt, IconArrowRight, IconChartBar, IconBrain, IconTarget, IconUsers, IconBriefcase, IconUserCheck, IconBrandGithub, IconBrandTwitter, IconBrandLinkedin, IconActivity } from '@tabler/icons-react';
import { Link } from 'react-router-dom';

const fadeUp = {
  hidden:  { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
};

const stagger = {
  hidden:  {},
  visible: { transition: { staggerChildren: 0.12 } },
};

export default function LandingPage() {
  return (
    <div style={{ minHeight: '100vh' }}>

      {/* ────────────────── HERO ────────────────── */}
      <section style={{ position: 'relative', overflow: 'hidden' }}>
        {/* subtle grid bg */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.03) 1px, transparent 0)',
          backgroundSize: '40px 40px',
          pointerEvents: 'none',
        }} />
        {/* lime glow orb */}
        <div style={{
          position: 'absolute', top: '-200px', left: '50%',
          transform: 'translateX(-50%)',
          width: '600px', height: '600px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(200,255,0,0.07) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '7rem 1.5rem 6rem', position: 'relative', zIndex: 1 }}>
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            style={{ textAlign: 'center', maxWidth: '780px', margin: '0 auto' }}
          >
            <motion.div variants={fadeUp}>
              <span className="hero-badge">
                <span className="pulse-dot" />
                AI-Powered Portfolio Intelligence
              </span>
            </motion.div>

            <motion.h1
              variants={fadeUp}
              className="heading-xl"
              style={{ fontSize: 'clamp(2.5rem, 6vw, 4.5rem)', marginBottom: '1.25rem', color: 'var(--text-primary)' }}
            >
              Smarter investing,<br />
              <span className="gradient-text">powered by AI</span>
            </motion.h1>

            <motion.p
              variants={fadeUp}
              style={{
                fontSize: 'clamp(1rem, 2vw, 1.2rem)',
                color: 'var(--text-secondary)',
                marginBottom: '2.5rem',
                lineHeight: 1.7,
                maxWidth: '560px',
                margin: '0 auto 2.5rem',
              }}
            >
              Ensemble ML models, risk-adjusted portfolio optimization,
              and live Nifty 50 analytics — built for Indian markets.
            </motion.p>

            <motion.div variants={fadeUp} style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link to="/signup" className="btn-primary" style={{ fontSize: '0.95rem', padding: '0.75rem 2rem' }}>
                Start for free
                <IconArrowRight style={{ width: '16px', height: '16px' }} />
              </Link>
              <Link to="/dashboard" className="btn-secondary" style={{ fontSize: '0.95rem', padding: '0.75rem 2rem' }}>
                Live demo
              </Link>
            </motion.div>

            {/* Trust strip */}
            <motion.div
              variants={fadeUp}
              style={{ marginTop: '3rem', display: 'flex', justifyContent: 'center', gap: '2.5rem', flexWrap: 'wrap' }}
            >
              {[
                { value: '50+', label: 'Nifty 50 stocks' },
                { value: '4',   label: 'ML models' },
                { value: '10y', label: 'Backtest depth' },
                { value: '99%', label: 'Uptime' },
              ].map((s) => (
                <div key={s.label} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#c8ff00', fontFamily: "'Space Grotesk', sans-serif" }}>{s.value}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{s.label}</div>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ────────────────── FEATURES ────────────────── */}
      <section style={{ padding: '5rem 0', borderTop: '1px solid var(--border)' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 1.5rem' }}>
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger}>
            <motion.div variants={fadeUp} style={{ textAlign: 'center', marginBottom: '3rem' }}>
              <p style={{ fontSize: '0.8rem', fontWeight: 600, color: '#c8ff00', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>
                Capabilities
              </p>
              <h2 className="heading-lg" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.5rem)', color: 'var(--text-primary)' }}>
                Everything you need to trade smarter
              </h2>
            </motion.div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1px', border: '1px solid var(--border)', borderRadius: '12px', overflow: 'hidden' }}>
              {[
                {
                  icon: IconRobot,
                  title: 'ML Predictions',
                  desc: 'Ensemble of LSTM, Linear/Logistic Regression & SVM models trained on Nifty 50 — voted consensus signals.',
                },
                {
                  icon: IconChartBar,
                  title: 'Portfolio Optimization',
                  desc: 'Risk-adjusted allocation with automated rebalancing, efficient frontier analysis, and comprehensive backtesting.',
                },
                {
                  icon: IconShield,
                  title: 'Risk Management',
                  desc: 'Sharpe ratio, max drawdown, volatility analysis, and real-time risk metrics keep your exposure in check.',
                },
                {
                  icon: IconBolt,
                  title: 'Live Market Data',
                  desc: 'Real-time yfinance integration with RSI, MACD, Bollinger Bands, and 20+ technical indicators.',
                },
              ].map((f, i) => (
                <motion.div
                  key={i}
                  variants={fadeUp}
                  style={{
                    background: 'var(--bg-surface)',
                    padding: '2rem',
                    cursor: 'default',
                    transition: 'background 0.2s ease',
                  }}
                  whileHover={{ background: 'var(--bg-elevated)' }}
                >
                  <div className="feature-icon" style={{ marginBottom: '1.25rem' }}>
                    <f.icon style={{ width: '20px', height: '20px' }} />
                  </div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.6rem' }}>{f.title}</h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{f.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ────────────────── HOW IT WORKS ────────────────── */}
      <section style={{ padding: '5rem 0' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 1.5rem' }}>
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger}>
            <motion.div variants={fadeUp} style={{ textAlign: 'center', marginBottom: '3rem' }}>
              <p style={{ fontSize: '0.8rem', fontWeight: 600, color: '#c8ff00', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>
                Workflow
              </p>
              <h2 className="heading-lg" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.5rem)', color: 'var(--text-primary)' }}>
                Three steps to better returns
              </h2>
            </motion.div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem' }}>
              {[
                { step: '01', icon: IconTarget,    title: 'Connect',  desc: 'Link your portfolio or select from Nifty 50 stocks to begin analysis.' },
                { step: '02', icon: IconBrain,     title: 'Analyze',  desc: 'Our ensemble of ML models processes historical and live data to surface patterns.' },
                { step: '03', icon: IconTrendingUp,title: 'Optimize', desc: 'Receive actionable allocation recommendations and risk-adjusted strategies.' },
              ].map((item, i) => (
                <motion.div key={i} variants={fadeUp} className="card" style={{ position: 'relative' }}>
                  <div style={{
                    position: 'absolute', top: '1.5rem', right: '1.5rem',
                    fontFamily: "'Space Grotesk', sans-serif",
                    fontSize: '2.5rem', fontWeight: 700,
                    color: 'rgba(255,255,255,0.04)',
                    lineHeight: 1,
                  }}>{item.step}</div>
                  <div style={{
                    width: '40px', height: '40px', borderRadius: '8px',
                    background: 'rgba(200,255,0,0.08)',
                    border: '1px solid rgba(200,255,0,0.2)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    marginBottom: '1rem', color: '#c8ff00',
                  }}>
                    <item.icon style={{ width: '18px', height: '18px' }} />
                  </div>
                  <h3 style={{ fontWeight: 600, fontSize: '1.05rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>{item.title}</h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ────────────────── TECH STACK ────────────────── */}
      <section style={{ padding: '5rem 0', borderTop: '1px solid var(--border)' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 1.5rem' }}>
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger}>
            <motion.div variants={fadeUp} style={{ textAlign: 'center', marginBottom: '3rem' }}>
              <p style={{ fontSize: '0.8rem', fontWeight: 600, color: '#c8ff00', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>
                Stack
              </p>
              <h2 className="heading-lg" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.5rem)', color: 'var(--text-primary)' }}>
                Production-grade infrastructure
              </h2>
            </motion.div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
              {[
                { title: 'Backend',   tech: ['FastAPI', 'Python 3.11', 'TensorFlow', 'scikit-learn', 'yfinance'] },
                { title: 'Frontend',  tech: ['React 18', 'TypeScript', 'Vite', 'Tailwind CSS', 'Framer Motion'] },
                { title: 'ML Models', tech: ['LSTM Neural Net', 'Linear Regression', 'Logistic Regression', 'SVM'] },
              ].map((stack, i) => (
                <motion.div key={i} variants={fadeUp} className="card-flat">
                  <h3 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#c8ff00', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{stack.title}</h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {stack.tech.map((t, j) => (
                      <span key={j} className="badge badge-info">{t}</span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ────────────────── FOR WHO ────────────────── */}
      <section style={{ padding: '5rem 0' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 1.5rem' }}>
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger}>
            <motion.div variants={fadeUp} style={{ textAlign: 'center', marginBottom: '3rem' }}>
              <p style={{ fontSize: '0.8rem', fontWeight: 600, color: '#c8ff00', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>
                Who it's for
              </p>
              <h2 className="heading-lg" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.5rem)', color: 'var(--text-primary)' }}>
                Built for serious investors
              </h2>
            </motion.div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
              {[
                { icon: IconUsers,      title: 'Retail Investors',    desc: 'Data-driven decisions without needing a finance degree.' },
                { icon: IconBriefcase,  title: 'Portfolio Managers',  desc: 'Scalable risk-adjusted strategies for client portfolios.' },
                { icon: IconUserCheck,  title: 'Financial Advisors',  desc: 'ML-backed recommendations your clients can trust.' },
              ].map((u, i) => (
                <motion.div key={i} variants={fadeUp} className="card" style={{ textAlign: 'center' }}>
                  <div style={{
                    width: '48px', height: '48px', borderRadius: '10px',
                    background: 'rgba(200,255,0,0.06)',
                    border: '1px solid rgba(200,255,0,0.15)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    margin: '0 auto 1rem', color: '#c8ff00',
                  }}>
                    <u.icon style={{ width: '22px', height: '22px' }} />
                  </div>
                  <h3 style={{ fontWeight: 600, fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>{u.title}</h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{u.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ────────────────── CTA ────────────────── */}
      <section style={{ padding: '5rem 0', borderTop: '1px solid var(--border)' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 1.5rem' }}>
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeUp}
            style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border)',
              borderRadius: '16px',
              padding: 'clamp(2.5rem, 5vw, 4rem)',
              textAlign: 'center',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <div style={{
              position: 'absolute', inset: 0,
              background: 'radial-gradient(ellipse at 50% 0%, rgba(200,255,0,0.06) 0%, transparent 70%)',
              pointerEvents: 'none',
            }} />
            <div style={{ position: 'relative', zIndex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
                <div style={{
                  width: '56px', height: '56px', borderRadius: '12px',
                  background: 'rgba(200,255,0,0.1)',
                  border: '1px solid rgba(200,255,0,0.3)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#c8ff00',
                }}>
                  <IconActivity style={{ width: '26px', height: '26px' }} />
                </div>
              </div>
              <h2 className="heading-lg" style={{ fontSize: 'clamp(1.75rem, 4vw, 2.5rem)', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
                Ready to elevate your portfolio?
              </h2>
              <p style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '2rem', maxWidth: '440px', margin: '0 auto 2rem' }}>
                Join investors already using AI to make smarter decisions in Indian markets.
              </p>
              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <Link to="/signup" className="btn-primary" style={{ fontSize: '0.95rem', padding: '0.75rem 2rem' }}>
                  Get started free
                  <IconArrowRight style={{ width: '16px', height: '16px' }} />
                </Link>
                <Link to="/dashboard" className="btn-secondary" style={{ fontSize: '0.95rem', padding: '0.75rem 2rem' }}>
                  View demo
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ────────────────── FOOTER ────────────────── */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '3rem 0 2rem' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 1.5rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '2rem', marginBottom: '2.5rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <IconTrendingUp style={{ width: '18px', height: '18px', color: '#c8ff00' }} />
                <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '0.95rem' }}>
                  QuantFin<span style={{ color: '#c8ff00' }}>AI</span>
                </span>
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                AI-powered portfolio management for Indian markets.
              </p>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                {[
                  { icon: IconBrandTwitter,  href: 'https://twitter.com/quantfin_ai' },
                  { icon: IconBrandLinkedin, href: 'https://linkedin.com/company/quantfin-ai' },
                  { icon: IconBrandGithub,   href: 'https://github.com/abhi2k4/QuantFin' },
                ].map((s, i) => (
                  <a
                    key={i}
                    href={s.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      width: '32px', height: '32px', borderRadius: '7px',
                      border: '1px solid var(--border)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: 'var(--text-muted)',
                      transition: 'border-color 0.2s, color 0.2s',
                    }}
                    onMouseOver={e => {
                      (e.currentTarget as HTMLElement).style.borderColor = 'rgba(200,255,0,0.3)';
                      (e.currentTarget as HTMLElement).style.color = '#c8ff00';
                    }}
                    onMouseOut={e => {
                      (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)';
                      (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)';
                    }}
                  >
                    <s.icon style={{ width: '14px', height: '14px' }} />
                  </a>
                ))}
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Product</h4>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {[
                  { label: 'Dashboard',  to: '/dashboard' },
                  { label: 'Solutions',  to: '/solutions' },
                  { label: 'Technology', to: '/technology' },
                ].map(l => (
                  <li key={l.label}><Link to={l.to} style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{l.label}</Link></li>
                ))}
              </ul>
            </div>

            <div>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Company</h4>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {[
                  { label: 'Contact', to: '/contact' },
                  { label: 'About',   to: '/about' },
                ].map(l => (
                  <li key={l.label}><Link to={l.to} style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{l.label}</Link></li>
                ))}
              </ul>
            </div>

            <div>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Legal</h4>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {[
                  { label: 'Privacy Policy', to: '/privacy' },
                  { label: 'Terms of Service', to: '/terms' },
                  { label: 'Disclaimer',       to: '/disclaimer' },
                ].map(l => (
                  <li key={l.label}><Link to={l.to} style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{l.label}</Link></li>
                ))}
              </ul>
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>© 2025 QuantFin AI. All rights reserved.</p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Not financial advice. For educational purposes only.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
