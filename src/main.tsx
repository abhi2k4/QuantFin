import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ClerkProvider } from '@/lib/clerk';
import { ThemeProvider } from './components/theme-provider';
import App from './App.tsx';
import './index.css';
 
// Import your Clerk Publishable Key
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY && import.meta.env.VITE_SKIP_CLERK_AUTH !== 'true') {
  // Clerk is optional in development. When no publishable key is provided we run in "skip auth" mode.
  console.warn('VITE_CLERK_PUBLISHABLE_KEY not set — running without Clerk (dev skip auth)');
}
 
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <BrowserRouter>
        <ThemeProvider defaultTheme="dark" storageKey="quantfin-ui-theme">
          <App />
        </ThemeProvider>
      </BrowserRouter>
    </ClerkProvider>
  </StrictMode>
);
