import { useSession } from 'next-auth/react';
import { useState, useEffect } from 'react';
import LogTable from '../../components/LogTable';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function Logs() {
  const { data: session, status } = useSession();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (session) {
      fetchLogs();
    }
  }, [session]);

  const fetchLogs = async () => {
    try {
      const res = await fetch('/api/logs', {
        headers: { 
          'Authorization': `Bearer ${session.user.tenant_id}:${session.user.api_key}` 
        },
      });
      
      if (res.ok) {
        const data = await res.json();
        setLogs(Array.isArray(data) ? data : []);
      } else {
        toast.error('Failed to fetch logs');
      }
    } catch (error) {
      toast.error('Error fetching logs');
    } finally {
      setLoading(false);
    }
  };

  if (status === 'loading') {
    return (
      <div className="container">
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center space-x-3">
            <div className="spinner"></div>
            <span className="text-gray-600">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="container">
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-6">Please log in to access the admin console.</p>
          <Link href="/admin" className="btn-primary">
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Security Logs</h1>
            <p className="text-gray-600 mt-2">Monitor security events and audit trails</p>
          </div>
          <Link href="/admin" className="btn-secondary">
            ← Back to Dashboard
          </Link>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card text-center">
            <div className="text-2xl font-bold text-primary-600">
              {logs.filter(log => log.event_type === 'processed').length}
            </div>
            <div className="text-sm text-gray-600">Processed</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-red-600">
              {logs.filter(log => log.event_type === 'blocked').length}
            </div>
            <div className="text-sm text-gray-600">Blocked</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-orange-600">
              {logs.filter(log => log.event_type === 'redacted').length}
            </div>
            <div className="text-sm text-gray-600">Redacted</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {logs.filter(log => log.event_type === 'warned').length}
            </div>
            <div className="text-sm text-gray-600">Warned</div>
          </div>
        </div>

        {/* Log Table */}
        <LogTable logs={logs} loading={loading} />
      </div>
    </div>
  );
}
