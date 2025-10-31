import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { useState } from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  Brain,
  Menu,
  Sun,
  Moon,
  Lightbulb,
  Cpu,
  Users,
  BarChart3
  // LineChart
} from 'lucide-react';
import { Toaster } from 'sonner';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';

import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { useTheme } from '@/components/theme-provider';

// Pages
import LandingPage from '@/pages/LandingPage';
import Dashboard from '@/pages/Dashboard';
import ModelInsights from '@/pages/ModelInsights';
import BacktestResults from '@/pages/BacktestResults';
import BacktestPage from '@/pages/BacktestPage';
import SettingsPage from '@/pages/SettingsPage';
import Solutions from '@/pages/Solutions';
import Technology from '@/pages/Technology';
import About from '@/pages/About';
import Contact from '@/pages/Contact';
import Signup from '@/pages/Signup';
import Signin from '@/pages/Signin';
import Privacy from '@/pages/Privacy';
import Terms from '@/pages/Terms';
import Disclaimer from '@/pages/Disclaimer';
// import Analytics from '@/pages/dashboard/Analytics';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  // { icon: LineChart, label: 'Analytics', path: '/analytics' },
  { icon: Brain, label: 'Models', path: '/models' },
  { icon: BarChart3, label: 'Backtest', path: '/backtest' },
  { icon: Lightbulb, label: 'Solutions', path: '/solutions' },
  { icon: Cpu, label: 'Technology', path: '/technology' },
];

const pageVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 }
};

function App() {
  const location = useLocation();
  const { theme, setTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const NavLinks = ({ onClick }: { onClick?: () => void }) => (
    <nav className="space-y-3 p-4">
      {navItems.map((item) => {
        const isActive = location.pathname === item.path;
        return (
          <Link
            key={item.path}
            to={item.path}
            onClick={onClick}
            className={`flex items-center gap-3 px-5 py-3.5 rounded-2xl transition-all ${
              isActive
                ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );

  return (
    <div className="min-h-screen">
      {/* Toast Notifications */}
      <Toaster 
        position="top-right" 
        theme={theme === 'dark' ? 'dark' : 'light'}
        richColors 
      />
      
      {/* Top Navbar - Softer, more elegant */}
      <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-black/40 backdrop-blur-xl">
        <div className="container flex h-20 items-center px-6">
          {/* Mobile Menu */}
          <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden mr-2 hover:bg-white/5">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 bg-navy-900 border-navy-700">
              <div className="py-4">
                <h2 className="text-xl font-bold mb-6 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  QuantFin AI
                </h2>
                <NavLinks onClick={() => setSidebarOpen(false)} />
              </div>
            </SheetContent>
          </Sheet>

          {/* Logo */}
          <Link to="/" className="flex items-center gap-3">
            <TrendingUp className="w-7 h-7 text-blue-400" />
            <span className="text-xl font-bold gradient-text">
              QuantFin AI
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex mx-auto">
            <div className="flex items-center gap-1 bg-white/5 backdrop-blur-xl rounded-full p-1.5 border border-white/10">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-full transition-all text-xs font-medium ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                    title={item.label}
                  >
                    <item.icon className="w-4 h-4" />
                    <span className="hidden xl:inline">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Theme Toggle & CTA */}
          <div className="ml-auto flex items-center gap-4">
            <Link to="/contact" className="hidden md:block text-sm font-medium text-gray-400 hover:text-white transition-colors">
              Contact
            </Link>
            
            {/* Clerk Authentication */}
            <SignedOut>
              <Link to="/signup">
                <Button className="btn-primary px-6 py-2 text-sm rounded-xl">
                  Try QuantFin
                </Button>
              </Link>
            </SignedOut>
            <SignedIn>
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: 'w-10 h-10'
                  }
                }}
                afterSignOutUrl="/"
              />
            </SignedIn>
            
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="rounded-full w-10 h-10 hover:bg-white/10"
            >
              {theme === 'dark' ? (
                <Sun className="h-5 w-5 text-yellow-400" />
              ) : (
                <Moon className="h-5 w-5 text-slate-700" />
              )}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content - Remove container padding for full-width landing */}
      <main>
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route
              path="/"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <LandingPage />
                </motion.div>
              }
            />
            <Route
              path="/dashboard"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Dashboard />
                </motion.div>
              }
            />
            <Route
              path="/models"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <ModelInsights />
                </motion.div>
              }
            />
            {/* <Route
              path="/analytics"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Analytics />
                </motion.div>
              }
            /> */}
            <Route
              path="/backtest"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <BacktestPage />
                </motion.div>
              }
            />
            <Route
              path="/settings"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <SettingsPage />
                </motion.div>
              }
            />
            <Route
              path="/solutions"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Solutions />
                </motion.div>
              }
            />
            <Route
              path="/technology"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Technology />
                </motion.div>
              }
            />
            <Route
              path="/about"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <About />
                </motion.div>
              }
            />
            <Route
              path="/contact"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Contact />
                </motion.div>
              }
            />
            <Route
              path="/signup"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Signup />
                </motion.div>
              }
            />
            <Route
              path="/signin"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Signin />
                </motion.div>
              }
            />
            <Route
              path="/privacy"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Privacy />
                </motion.div>
              }
            />
            <Route
              path="/terms"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Terms />
                </motion.div>
              }
            />
            {/* <Route
              path="/dashboard/analytics"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Analytics />
                </motion.div>
              }
            /> */}
            <Route
              path="/disclaimer"
              element={
                <motion.div
                  variants={pageVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  transition={{ duration: 0.3 }}
                >
                  <Disclaimer />
                </motion.div>
              }
            />
          </Routes>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
