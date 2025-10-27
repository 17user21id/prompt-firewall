import Link from 'next/link';

/**
 * Navigation item component to reduce duplication
 */
function NavLink({ href, children, className = '', onClick }) {
  return (
    <Link 
      href={href}
      className={`text-white hover:text-primary-200 transition-colors duration-200 font-medium ${className}`}
      onClick={onClick}
    >
      {children}
    </Link>
  );
}

/**
 * Navigation section for desktop
 */
export function DesktopNav({ session, tenantSession, onLogout, onToggleDarkMode, darkMode }) {
  const isLoggedIn = session || tenantSession;

  return (
    <div className="hidden md:flex items-center space-x-6">
      <NavLink href="/">Prompt Test</NavLink>
      
      {isLoggedIn ? (
        <>
          {session && (
            <NavLink href="/admin">Admin Console</NavLink>
          )}
          <div className="flex items-center space-x-4">
            {session && (
              <span className="text-primary-200 text-sm">
                Welcome, {session.user.name}
              </span>
            )}
            {tenantSession && (
              <span className="text-primary-200 text-sm">
                {tenantSession.tenantName}
              </span>
            )}
            <button 
              onClick={onLogout}
              className="text-white hover:text-primary-200 transition-colors duration-200 font-medium"
            >
              Logout
            </button>
          </div>
        </>
      ) : (
        <NavLink href="/login">Login</NavLink>
      )}
      
      {/* Dark Mode Toggle */}
      <button
        onClick={onToggleDarkMode}
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
  );
}

/**
 * Mobile menu button
 */
export function MobileMenuButton({ isOpen, onClick }) {
  return (
    <div className="md:hidden">
      <button
        onClick={onClick}
        className="text-white hover:text-primary-200 focus:outline-none focus:text-primary-200"
        aria-label="Toggle mobile menu"
      >
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          {isOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>
    </div>
  );
}

/**
 * Mobile navigation menu
 */
export function MobileNav({ isOpen, session, tenantSession, onLogout, onToggleDarkMode, darkMode, closeMenu }) {
  if (!isOpen) return null;

  const isLoggedIn = session || tenantSession;

  return (
    <div className="md:hidden bg-primary-700 dark:bg-primary-800 border-t border-primary-500">
      <div className="px-2 pt-2 pb-3 space-y-1">
        <NavLink href="/" onClick={closeMenu}>Prompt Test</NavLink>
        
        {isLoggedIn ? (
          <>
            {session && (
              <NavLink href="/admin" onClick={closeMenu}>Admin Console</NavLink>
            )}
            <div className="px-3 py-2 border-t border-primary-500">
              {session && (
                <div className="text-primary-200 text-sm mb-2">
                  Welcome, {session.user.name}
                </div>
              )}
              {tenantSession && (
                <div className="text-primary-200 text-sm mb-2">
                  {tenantSession.tenantName}
                </div>
              )}
              <button 
                onClick={() => {
                  onLogout();
                  closeMenu();
                }}
                className="text-white hover:text-primary-200 transition-colors duration-200"
              >
                Logout
              </button>
            </div>
          </>
        ) : (
          <NavLink href="/login" onClick={closeMenu}>Login</NavLink>
        )}
        
        <div className="px-3 py-2 border-t border-primary-500">
          <button
            onClick={() => {
              onToggleDarkMode();
              closeMenu();
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
  );
}

