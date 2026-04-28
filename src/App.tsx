import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { useState } from 'react';
import { IconLayoutDashboard, IconTrendingUp, IconBrain, IconMenu2, IconChartBar, IconBulb, IconCpu, IconX } from '@tabler/icons-react';
import { Toaster } from 'sonner';
import { SignedIn, SignedOut, UserButton } from '@/lib/clerk';

// Pages
import LandingPage   from '@/pages/LandingPage';
import Dashboard     from '@/pages/Dashboard';
import ModelInsights from '@/pages/ModelInsights';
import BacktestPage  from '@/pages/BacktestPage';
import SettingsPage  from '@/pages/SettingsPage';
import Solutions     from '@/pages/Solutions';
import Technology    from '@/pages/Technology';
import About         from '@/pages/About';
import Contact       from '@/pages/Contact';
import Signup        from '@/pages/Signup';
import Signin        from '@/pages/Signin';
import Privacy       from '@/pages/Privacy';
import Terms         from '@/pages/Terms';
import Disclaimer    from '@/pages/Disclaimer';

const navItems = [
  { icon: IconLayoutDashboard, label: 'Dashboard',  path: '/dashboard' },
  { icon: IconBrain,           label: 'Models',     path: '/models'    },
  { icon: IconChartBar,       label: 'Backtest',   path: '/backtest'  },
  { icon: IconBulb,       label: 'Solutions',  path: '/solutions' },
  { icon: IconCpu,             label: 'Technology', path: '/technology'},
];

const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit:    { opacity: 0, y: -8 },
};

function App() {
  const location   = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-base)' }}>
      <Toaster position="top-right" theme="dark" richColors />

      {/* ── TOP NAV ── */}
      <header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 50,
          background: 'rgba(13,13,13,0.88)',
          backdropFilter: 'blur(18px)',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <div
          style={{
            maxWidth: '1280px',
            margin: '0 auto',
            padding: '0 1.5rem',
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            gap: '2rem',
          }}
        >
          {/* Logo */}
          <Link
            to="/"
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}
          >
            <IconTrendingUp style={{ width: '20px', height: '20px', color: '#c8ff00' }} />
            <span
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700,
                fontSize: '1rem',
                color: '#f5f5f5',
                letterSpacing: '-0.01em',
              }}
            >
              QuantFin<span style={{ color: '#c8ff00' }}>AI</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex" style={{ flex: 1, justifyContent: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`nav-link${isActive ? ' active' : ''}`}
                  >
                    <item.icon style={{ width: '15px', height: '15px' }} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </nav>

          {/* Right side */}
          <div
            style={{
              marginLeft: 'auto',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              flexShrink: 0,
            }}
          >
            <Link
              to="/contact"
              className="hidden md:block"
              style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}
            >
              Contact
            </Link>

            <SignedOut>
              <Link
                to="/signin"
                className="hidden md:block"
                style={{
                  fontSize: '0.85rem',
                  color: 'var(--text-secondary)',
                  padding: '0.45rem 0.85rem',
                  borderRadius: '6px',
                  transition: 'color 0.2s',
                }}
              >
                Sign in
              </Link>
              <Link
                to="/signup"
                className="btn-primary"
                style={{ fontSize: '0.82rem', padding: '0.5rem 1.2rem' }}
              >
                Get started
              </Link>
            </SignedOut>

            <SignedIn>
              <UserButton
                appearance={{ elements: { avatarBox: 'w-8 h-8' } }}
                afterSignOutUrl="/"
              />
            </SignedIn>

            {/* Mobile toggle */}
            <button
              className="md:hidden btn-ghost"
              style={{ padding: '0.4rem' }}
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label="Toggle menu"
            >
              {mobileOpen
                ? <IconX style={{ width: '20px', height: '20px' }} />
                : <IconMenu2 style={{ width: '20px', height: '20px' }} />}
            </button>
          </div>
        </div>

        {/* Mobile drawer */}
        <AnimatePresence>
          {mobileOpen && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.18 }}
              style={{
                background: 'var(--bg-surface)',
                borderBottom: '1px solid var(--border)',
                padding: '1rem 1.5rem',
              }}
            >
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileOpen(false)}
                    className={`nav-link${isActive ? ' active' : ''}`}
                    style={{ display: 'flex', padding: '0.65rem 0.85rem', marginBottom: '0.25rem' }}
                  >
                    <item.icon style={{ width: '16px', height: '16px' }} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
              <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem' }}>
                <SignedOut>
                  <Link
                    to="/signin"
                    onClick={() => setMobileOpen(false)}
                    className="btn-secondary"
                    style={{ flex: 1, justifyContent: 'center' }}
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/signup"
                    onClick={() => setMobileOpen(false)}
                    className="btn-primary"
                    style={{ flex: 1, justifyContent: 'center' }}
                  >
                    Get started
                  </Link>
                </SignedOut>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* ── PAGES ── */}
      <main>
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            {/* Public */}
            <Route path="/"           element={<Wrap><LandingPage /></Wrap>} />
            <Route path="/solutions"  element={<Wrap><Solutions /></Wrap>} />
            <Route path="/technology" element={<Wrap><Technology /></Wrap>} />
            <Route path="/about"      element={<Wrap><About /></Wrap>} />
            <Route path="/contact"    element={<Wrap><Contact /></Wrap>} />
            <Route path="/privacy"    element={<Wrap><Privacy /></Wrap>} />
            <Route path="/terms"      element={<Wrap><Terms /></Wrap>} />
            <Route path="/disclaimer" element={<Wrap><Disclaimer /></Wrap>} />

            {/* Auth */}
            <Route path="/signup"  element={<Wrap><Signup /></Wrap>} />
            <Route path="/signin"  element={<Wrap><Signin /></Wrap>} />

            {/* App — open access (no auth gate) */}
            <Route path="/dashboard" element={<Wrap><Dashboard /></Wrap>} />
            <Route path="/models"    element={<Wrap><ModelInsights /></Wrap>} />
            <Route path="/backtest"  element={<Wrap><BacktestPage /></Wrap>} />
            <Route path="/settings"  element={<Wrap><SettingsPage /></Wrap>} />
          </Routes>
        </AnimatePresence>
      </main>
    </div>
  );
}

function Wrap({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.22, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
}

export default App;
