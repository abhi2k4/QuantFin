import { motion } from 'framer-motion';
import type { Variants } from 'framer-motion';
import { IconTrendingUp, IconArrowLeft } from '@tabler/icons-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
};

export default function Signin() {
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
        {/* Subtle glow */}
        <div style={{
          position: 'absolute', bottom: '-100px', left: '-100px',
          width: '400px', height: '400px', borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(200,255,0,0.06) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '3rem' }}>
            <IconTrendingUp style={{ width: '20px', height: '20px', color: '#c8ff00' }} />
            <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1rem' }}>
              QuantFin<span style={{ color: '#c8ff00' }}>AI</span>
            </span>
          </Link>

          <h2 style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1.75rem', lineHeight: 1.2, color: 'var(--text-primary)', marginBottom: '1rem' }}>
            Welcome back
          </h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Sign in to access your AI-powered portfolio dashboard and live Nifty 50 analytics.
          </p>
        </div>

        <div>
          {[
            { stat: '50+', label: 'Tracked stocks' },
            { stat: '4', label: 'ML models' },
            { stat: '10y', label: 'Backtest data' },
          ].map((s) => (
            <div key={s.label} style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
              <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: '1.5rem', color: '#c8ff00', minWidth: '60px' }}>{s.stat}</span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right panel — auth form */}
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
            <IconArrowLeft style={{ width: '14px', height: '14px' }} />
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
            Sign in
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            Don't have an account?{' '}
            <Link to="/signup" style={{ color: '#c8ff00', fontWeight: 500 }}>
              Sign up
            </Link>
          </p>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              alert('Signin form submitted. Implement your auth logic here.');
            }}
            style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}
          >
            <div>
              <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.5rem' }}>
                Email
              </label>
              <input
                type="email"
                placeholder="your@email.com"
                required
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.5rem' }}>
                Password
              </label>
              <input
                type="password"
                placeholder="••••••••"
                required
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            <Link
              to="#"
              style={{
                fontSize: '0.85rem',
                color: '#c8ff00',
                textDecoration: 'none',
                textAlign: 'right',
                marginTop: '-0.5rem',
              }}
            >
              Forgot password?
            </Link>

            <button
              type="submit"
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                background: '#c8ff00',
                color: '#000',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: 'pointer',
                transition: 'background 0.2s',
                marginTop: '0.5rem',
              }}
              onMouseOver={(e) => (e.currentTarget.style.background = '#d8ff33')}
              onMouseOut={(e) => (e.currentTarget.style.background = '#c8ff00')}
            >
              Sign in
            </button>
          </form>
        </div>
      </div>
    </motion.div>
  );
}
