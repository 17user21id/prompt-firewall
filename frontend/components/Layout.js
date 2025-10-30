import { useSession, signOut } from 'next-auth/react';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { getSession, clearSession } from '../lib/session';
import { DesktopNav, MobileMenuButton, MobileNav } from './Layout/Navigation';
import { SESSION_CONFIG } from '../lib/constants';

export default function Layout({ children }) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [tenantSession, setTenantSession] = useState(null);

  // Check for tenant session
  useEffect(() => {
    const checkTenantSession = () => {
      const tenant = getSession();
      setTenantSession(tenant);
    };
    
    checkTenantSession();
    // Check periodically in case session changes
    const interval = setInterval(checkTenantSession, SESSION_CONFIG.CHECK_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Check for saved theme preference or default to dark mode
    const savedDarkMode = localStorage.getItem('darkMode');
    // Default to dark mode if not saved
    const isDark = savedDarkMode === null ? true : savedDarkMode === 'true';
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode);
    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleLogout = () => {
    if (tenantSession) {
      clearSession();
      setTenantSession(null);
      router.push('/login');
    } else if (session) {
      signOut();
    }
  };

  const isLoggedIn = session || tenantSession;

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-primary-600 dark:bg-primary-800 shadow-lg transition-colors duration-300">
        <div className="container">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <span className="text-primary-600 font-bold text-lg">🛡️</span>
              </div>
              <span className="text-xl font-bold text-white">Prompt Firewall</span>
            </Link>

            {/* Desktop Navigation */}
            <DesktopNav 
              session={session}
              tenantSession={tenantSession}
              onLogout={handleLogout}
              onToggleDarkMode={toggleDarkMode}
              darkMode={darkMode}
            />

            {/* Mobile menu button */}
            <MobileMenuButton 
              isOpen={mobileMenuOpen}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            />
          </div>

          {/* Mobile Navigation */}
          <MobileNav 
            isOpen={mobileMenuOpen}
            session={session}
            tenantSession={tenantSession}
            onLogout={handleLogout}
            onToggleDarkMode={toggleDarkMode}
            darkMode={darkMode}
            closeMenu={() => setMobileMenuOpen(false)}
          />
        </div>
      </nav>

      {/* Main Content */}
      <main className="container py-8 animate-fade-in flex-1">
        <div className="transition-opacity duration-300">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto transition-colors duration-300">
        <div className="container py-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-600 dark:text-gray-400 text-sm">
              © 2024 Prompt Firewall MVP. Built for AI Security.
            </div>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <span 
                className="text-gray-600 dark:text-gray-400 text-sm cursor-default"
              >
                Documentation
              </span>
              <span 
                className="text-gray-600 dark:text-gray-400 text-sm cursor-default"
              >
                API Reference
              </span>
              <span 
                className="text-gray-600 dark:text-gray-400 text-sm cursor-default"
              >
                System Status
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
