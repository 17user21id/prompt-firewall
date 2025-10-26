import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import LoginForm from '../../components/LoginForm';
import { useEffect } from 'react';

export default function AdminDashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'authenticated' && session) {
      router.push('/admin/dashboard');
    }
  }, [status, session, router]);

  if (status === 'loading') {
    return (
      <div className="container">
        <div className="flex items-center justify-center min-h-screen">
          <div className="flex items-center space-x-3">
            <div className="spinner"></div>
            <span className="text-gray-600">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'authenticated' && session) {
    return (
      <div className="container">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Admin Console</h1>
          
          <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <div className="flex items-center">
              <span className="text-green-600 dark:text-green-400 text-lg mr-2">✅</span>
              <span className="text-green-800 dark:text-green-300 font-medium">
                Welcome back, {session.user.name}!
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Link href="/admin/tenants" className="card hover:shadow-md transition-shadow duration-200">
              <div className="text-center">
                <div className="text-4xl mb-3">👥</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Manage Tenants</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Create and manage tenant accounts with secure authentication.
                </p>
              </div>
            </Link>

            <Link href="/admin/rules" className="card hover:shadow-md transition-shadow duration-200">
              <div className="text-center">
                <div className="text-4xl mb-3">⚙️</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Manage Rules</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Configure detection rules for PII and injection patterns.
                </p>
              </div>
            </Link>

            <Link href="/admin/logs" className="card hover:shadow-md transition-shadow duration-200">
              <div className="text-center">
                <div className="text-4xl mb-3">📋</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">View Logs</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Monitor security events and export audit logs.
                </p>
              </div>
            </Link>

            <Link href="/admin/analytics" className="card hover:shadow-md transition-shadow duration-200">
              <div className="text-center">
                <div className="text-4xl mb-3">📊</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Analytics</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  View security metrics and risk trends.
                </p>
              </div>
            </Link>

            <Link href="/admin/settings" className="card hover:shadow-md transition-shadow duration-200">
              <div className="text-center">
                <div className="text-4xl mb-3">🔧</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Settings</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Configure system settings and preferences.
                </p>
              </div>
            </Link>

            <Link href="/" className="card hover:shadow-md transition-shadow duration-200">
              <div className="text-center">
                <div className="text-4xl mb-3">🧪</div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Test Demo</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Try the public demo to test the firewall.
                </p>
              </div>
            </Link>
          </div>

          {/* Quick Stats */}
          <div className="mt-8 card">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Stats</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">0</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Requests</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">0</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Allowed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">0</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Blocked</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">0</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Redacted</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Admin Console</h1>
          <p className="text-gray-600 dark:text-gray-300">Sign in to access the admin dashboard</p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
