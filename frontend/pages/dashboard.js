import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import toast from 'react-hot-toast';
import { getSession } from '../lib/session';
import { fetchLogs, fetchRules } from '../lib/apiHelpers';
import { calculateStats } from '../lib/utils';
import { ERROR_MESSAGES } from '../lib/constants';
import { LoadingSpinner } from '../components/common';
import LogTable from '../components/LogTable';
import Badge from '../components/common/Badge';

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
    const session = getSession();
    
    if (!session) {
      toast.error(ERROR_MESSAGES.SESSION_EXPIRED);
      router.push('/login');
      return;
    }
    
    setTenantInfo({ tenant_id: session.tenantId, api_key: session.apiKey, name: session.tenantName });
    loadData(session.tenantId, session.apiKey);
  }, [router]);

  const loadData = async (tenantId, apiKey) => {
    setLoading(true);
    try {
      const [logsData, rulesData] = await Promise.all([
        fetchLogs(tenantId, apiKey),
        fetchRules(tenantId, apiKey)
      ]);
      
      setLogs(logsData);
      setRules(rulesData);
      setStats(calculateStats(logsData));
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error(error.message || ERROR_MESSAGES.API_ERROR);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !tenantInfo) {
    return <LoadingSpinner message="Loading dashboard..." />;
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
                      <Badge variant={rule.action || 'default'}>{rule.action}</Badge>
                      <Badge severity={rule.severity}>{rule.severity}</Badge>
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

