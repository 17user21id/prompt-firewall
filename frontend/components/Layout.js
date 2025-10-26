import { useSession, signOut } from 'next-auth/react';
import Link from 'next/link';
import { useState } from 'react';

export default function Layout({ children }) {
  const { data: session, status } = useSession();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-primary-600 shadow-lg">
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
                  href="/admin" 
                  className="text-white hover:text-primary-200 transition-colors duration-200 font-medium"
                >
                  Admin Login
                </Link>
              )}
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
            <div className="md:hidden bg-primary-700 border-t border-primary-500">
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
                    href="/admin" 
                    className="block px-3 py-2 text-white hover:text-primary-200 transition-colors duration-200"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Admin Login
                  </Link>
                )}
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
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="container py-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-600 text-sm">
              © 2024 Prompt Firewall MVP. Built for AI Security.
            </div>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a 
                href="/docs" 
                className="text-gray-600 hover:text-primary-600 text-sm transition-colors duration-200"
              >
                Documentation
              </a>
              <a 
                href="/api-docs" 
                className="text-gray-600 hover:text-primary-600 text-sm transition-colors duration-200"
              >
                API Reference
              </a>
              <a 
                href="/health" 
                className="text-gray-600 hover:text-primary-600 text-sm transition-colors duration-200"
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
