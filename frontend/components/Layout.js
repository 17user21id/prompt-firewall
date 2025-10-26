import { useSession, signOut } from 'next-auth/react';
import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function Layout({ children }) {
  const { data: session, status } = useSession();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // Check for saved theme preference or default to light mode
    const isDark = localStorage.getItem('darkMode') === 'true';
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

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Navigation */}
      <nav className="bg-primary-600 dark:bg-primary-800 shadow-lg">
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
            <div className="hidden md:flex items-center space-x-6">
              <Link 
                href="/" 
                className="text-white hover:text-primary-200 transition-colors duration-200 font-medium"
              >
                Demo
              </Link>
              {session ? (
                <>
                  <Link 
                    href="/admin" 
                    className="text-white hover:text-primary-200 transition-colors duration-200 font-medium"
                  >
                    Admin Console
                  </Link>
                  <div className="flex items-center space-x-4">
                    <span className="text-primary-200 text-sm">
                      Welcome, {session.user.name}
                    </span>
                    <button 
                      onClick={() => signOut()}
                      className="text-white hover:text-primary-200 transition-colors duration-200 font-medium"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <Link 
                  href="/login" 
                  className="text-white hover:text-primary-200 transition-colors duration-200 font-medium"
                >
                  Login
                </Link>
              )}
              
              {/* Dark Mode Toggle */}
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg text-white hover:bg-primary-700 dark:hover:bg-primary-900 transition-colors duration-200"
                aria-label="Toggle dark mode"
              >
                {darkMode ? (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-white hover:text-primary-200 focus:outline-none focus:text-primary-200"
                aria-label="Toggle mobile menu"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {mobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden bg-primary-700 dark:bg-primary-800 border-t border-primary-500">
              <div className="px-2 pt-2 pb-3 space-y-1">
                <Link 
                  href="/" 
                  className="block px-3 py-2 text-white hover:text-primary-200 transition-colors duration-200"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Demo
                </Link>
                {session ? (
                  <>
                    <Link 
                      href="/admin" 
                      className="block px-3 py-2 text-white hover:text-primary-200 transition-colors duration-200"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Admin Console
                    </Link>
                    <div className="px-3 py-2 border-t border-primary-500">
                      <div className="text-primary-200 text-sm mb-2">
                        Welcome, {session.user.name}
                      </div>
                      <button 
                        onClick={() => {
                          signOut();
                          setMobileMenuOpen(false);
                        }}
                        className="text-white hover:text-primary-200 transition-colors duration-200"
                      >
                        Logout
                      </button>
                    </div>
                  </>
                ) : (
                  <Link 
                    href="/login" 
                    className="block px-3 py-2 text-white hover:text-primary-200 transition-colors duration-200"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Login
                  </Link>
                )}
                <div className="px-3 py-2 border-t border-primary-500">
                  <button
                    onClick={() => {
                      toggleDarkMode();
                      setMobileMenuOpen(false);
                    }}
                    className="flex items-center space-x-2 text-white hover:text-primary-200 transition-colors duration-200 w-full"
                  >
                    {darkMode ? (
                      <>
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        <span>Light Mode</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                        </svg>
                        <span>Dark Mode</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="container py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
        <div className="container py-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-600 dark:text-gray-400 text-sm">
              © 2024 Prompt Firewall MVP. Built for AI Security.
            </div>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a 
                href="/docs" 
                className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 text-sm transition-colors duration-200"
              >
                Documentation
              </a>
              <a 
                href="/api-docs" 
                className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 text-sm transition-colors duration-200"
              >
                API Reference
              </a>
              <a 
                href="/health" 
                className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 text-sm transition-colors duration-200"
              >
                System Status
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
