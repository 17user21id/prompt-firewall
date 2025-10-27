import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { getSession, clearSession } from '../lib/session';
import LogTable from '../components/LogTable';

export default function Dashboard() {
  const router = useRouter();
  const [tenantInfo, setTenantInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState([]);
  const [rules, setRules] = useState([]);
  const [stats, setStats] = useState({
    totalPrompts: 0,
    blockedPrompts: 0,
    redactedPrompts: 0,
    allowedPrompts: 0
  });

  useEffect(() => {
    // Check if user is logged in and session is valid
    const session = getSession();
    
    if (!session) {
      toast.error('Session expired. Please login again.');
      router.push('/login');
      return;
    }
    
    setTenantInfo({ tenant_id: session.tenantId, api_key: session.apiKey, name: session.tenantName });
    loadData(session.tenantId, session.apiKey);
  }, [router]);

  const loadData = async (tenantId, apiKey) => {
    setLoading(true);
    try {
      // Load logs
      const logsResponse = await fetch(`/api/logs?tenant_id=${tenantId}`, {
        headers: {
          'Authorization': `Bearer ${tenantId}:${apiKey}`
        }
      });
      
      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        // API returns array directly
        setLogs(Array.isArray(logsData) ? logsData : logsData.logs || []);
        calculateStats(Array.isArray(logsData) ? logsData : logsData.logs || []);
      }
      
      // Load rules
      const rulesResponse = await fetch(`/api/rules?tenant_id=${tenantId}`, {
        headers: {
          'Authorization': `Bearer ${tenantId}:${apiKey}`
        }
      });
      
      if (rulesResponse.ok) {
        const rulesData = await rulesResponse.json();
        // API returns array directly
        setRules(Array.isArray(rulesData) ? rulesData : rulesData.rules || []);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (logData) => {
    const stats = {
      totalPrompts: logData.length,
      blockedPrompts: 0,
      redactedPrompts: 0,
      allowedPrompts: 0
    };
    
    logData.forEach(log => {
      if (log.event_type === 'blocked') {
        stats.blockedPrompts++;
      } else if (log.event_type === 'redacted' || log.event_type === 'warned') {
        stats.redactedPrompts++;
      } else if (log.event_type === 'processed') {
        stats.allowedPrompts++;
      }
    });
    
    setStats(stats);
  };

  const handleLogout = () => {
    clearSession();
    router.push('/login');
  };

  if (loading || !tenantInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center animate-fade-in">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Dashboard Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Dashboard - {tenantInfo.name}
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Monitor your prompt security and activity
        </p>
      </div>

        {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8 animate-slide-up">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 transition-all duration-300 hover:shadow-md">
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Prompts</div>
            <div className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">{stats.totalPrompts}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 transition-all duration-300 hover:shadow-md">
            <div className="text-sm font-medium text-red-600 dark:text-red-400">Blocked</div>
            <div className="mt-2 text-3xl font-semibold text-red-600 dark:text-red-400">{stats.blockedPrompts}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 transition-all duration-300 hover:shadow-md">
            <div className="text-sm font-medium text-yellow-600 dark:text-yellow-400">Redacted</div>
            <div className="mt-2 text-3xl font-semibold text-yellow-600 dark:text-yellow-400">{stats.redactedPrompts}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 transition-all duration-300 hover:shadow-md">
            <div className="text-sm font-medium text-green-600 dark:text-green-400">Allowed</div>
            <div className="mt-2 text-3xl font-semibold text-green-600 dark:text-green-400">{stats.allowedPrompts}</div>
          </div>
        </div>

        {/* Logs */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Recent Prompts</h2>
          <LogTable logs={logs} loading={loading} />
        </div>

        {/* Rules */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow transition-all duration-300">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 transition-colors duration-300">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Active Rules</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {rules.map((rule, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 transition-all duration-300 hover:shadow-md">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">{rule.type}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-300">{rule.description}</p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className={`px-3 py-1 text-xs rounded-full ${
                        rule.action === 'block' ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300' :
                        rule.action === 'redact' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300' :
                        'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300'
                      }`}>
                        {rule.action}
                      </span>
                      <span className={`px-3 py-1 text-xs rounded-full ${
                        rule.severity === 'high' ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300' :
                        rule.severity === 'medium' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300' :
                        'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                      }`}>
                        {rule.severity}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
    </div>
  );
}

