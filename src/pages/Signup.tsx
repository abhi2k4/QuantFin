import { motion } from 'framer-motion';
import { ArrowLeft, TrendingUp, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { SignUp } from '@/lib/clerk';

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
};

const perks = [
  'Live Nifty 50 portfolio analytics',
  'Ensemble ML prediction signals',
  'Risk-adjusted backtesting engine',
  'No credit card required',
];

export default function Signup() {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeUp}
      style={{ minHeight: 'calc(100vh - 60px)', display: 'flex' }}
    >
      {/* Left panel — branding */}
      <div
        className="hidden md:flex"
        style={{
          width: '400px',
          flexShrink: 0,
          background: 'var(--bg-surface)',
          borderRight: '1px solid var(--border)',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '3rem',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div style={{
          position: 'absolute', bottom: '-100px', left: '-100px',
          width: '400px', height: '400px', borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(200,255,0,0.06) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '3rem' }}>
            <TrendingUp style={{ width: '20px', height: '20px', color: '#c8ff00' }} />
            <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1rem' }}>
              QuantFin<span style={{ color: '#c8ff00' }}>AI</span>
            </span>
          </Link>

          <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1.75rem', lineHeight: 1.2, color: 'var(--text-primary)', marginBottom: '1rem' }}>
            Start investing smarter
          </h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '2rem' }}>
            Free access to AI-powered portfolio tools built specifically for Indian markets.
          </p>

          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
            {perks.map((perk) => (
              <li key={perk} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <CheckCircle2 style={{ width: '17px', height: '17px', color: '#c8ff00', flexShrink: 0 }} />
                <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{perk}</span>
              </li>
            ))}
          </ul>
        </div>

        <div style={{
          background: 'rgba(200,255,0,0.04)',
          border: '1px solid rgba(200,255,0,0.12)',
          borderRadius: '10px',
          padding: '1.25rem',
        }}>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            "QuantFin's ML ensemble cut my portfolio volatility by 30% while maintaining returns. The backtest data is a game-changer."
          </p>
          <p style={{ fontSize: '0.78rem', color: '#c8ff00', marginTop: '0.75rem', fontWeight: 500 }}>— Retail Investor, Mumbai</p>
        </div>
      </div>

      {/* Right panel — form */}
      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1.5rem',
        flexDirection: 'column',
      }}>
        <div style={{ width: '100%', maxWidth: '400px' }}>
          <Link
            to="/"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              fontSize: '0.82rem',
              color: 'var(--text-muted)',
              marginBottom: '2.5rem',
              transition: 'color 0.2s',
            }}
            onMouseOver={e => (e.currentTarget.style.color = '#c8ff00')}
            onMouseOut={e => (e.currentTarget.style.color = 'var(--text-muted)')}
          >
            <ArrowLeft style={{ width: '14px', height: '14px' }} />
            Back to home
          </Link>

          <h1
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: 700,
              fontSize: '1.75rem',
              color: 'var(--text-primary)',
              marginBottom: '0.5rem',
            }}
          >
            Create account
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            Already have an account?{' '}
            <Link to="/signin" style={{ color: '#c8ff00', fontWeight: 500 }}>
              Sign in
            </Link>
          </p>

          <SignUp
            appearance={{
              layout: { logoPlacement: 'none', showOptionalFields: false },
              elements: {
                rootBox: 'w-full',
                card: 'bg-transparent shadow-none border-0 p-0 w-full',
                headerTitle: 'hidden',
                headerSubtitle: 'hidden',
                socialButtonsBlockButton: [
                  'w-full bg-transparent border border-white/10 text-white',
                  'hover:bg-white/5 hover:border-white/20 rounded-lg h-11 text-sm font-medium',
                  'transition-all duration-200'
                ].join(' '),
                dividerLine: 'bg-white/8',
                dividerText: 'text-xs text-zinc-600',
                formFieldLabel: 'text-zinc-400 text-sm mb-1',
                formFieldInput: [
                  'bg-zinc-900 border border-white/8 text-white rounded-lg h-11 px-4 text-sm',
                  'focus:border-[#c8ff00]/50 focus:ring-2 focus:ring-[#c8ff00]/10',
                  'placeholder:text-zinc-600 transition-all duration-200'
                ].join(' '),
                formButtonPrimary: [
                  'w-full h-11 bg-[#c8ff00] text-black font-semibold rounded-lg text-sm',
                  'hover:bg-[#d8ff33] transition-all duration-200',
                  'focus:ring-2 focus:ring-[#c8ff00]/30'
                ].join(' '),
                footerActionLink: 'text-[#c8ff00] hover:text-[#d8ff33] font-medium',
                identityPreviewEditButton: 'text-[#c8ff00]',
                formFieldInputShowPasswordButton: 'text-zinc-500 hover:text-zinc-300',
                alertText: 'text-sm',
                formFieldErrorText: 'text-red-400 text-xs mt-1',
              },
            }}
            routing="path"
            path="/signup"
            signInUrl="/signin"
            afterSignUpUrl="/dashboard"
          />
        </div>
      </div>
    </motion.div>
  );
}
