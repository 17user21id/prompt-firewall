import { useState, useEffect, useMemo } from 'react';
import { TYPE_LABELS } from '../lib/constants';
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
  const [openGroups, setOpenGroups] = useState({});

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

  // Group rules by type for the Active Rules section
  const groupedRules = useMemo(() => {
    const groups = rules.reduce((acc, rule) => {
      const key = rule.type || 'OTHER';
      if (!acc[key]) acc[key] = [];
      acc[key].push(rule);
      return acc;
    }, {});
    return groups;
  }, [rules]);

  const toggleGroup = (groupKey) => {
    setOpenGroups((prev) => ({ ...prev, [groupKey]: !prev[groupKey] }));
  };

  const getTypeLabel = (type) => TYPE_LABELS[type] || type;

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

        {/* Active Rules - Grouped by Type */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow transition-all duration-300">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 transition-colors duration-300">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Active Rules</h2>
          </div>
          <div className="p-6 space-y-4">
            {Object.keys(groupedRules).length === 0 && (
              <div className="text-sm text-gray-500 dark:text-gray-400">No active rules found.</div>
            )}

            {Object.keys(groupedRules).sort().map((groupKey) => {
              const items = groupedRules[groupKey];
              const isOpen = openGroups[groupKey] ?? true;
              return (
                <div key={groupKey} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleGroup(groupKey)}
                    className="w-full flex items-center justify-between px-5 py-4 bg-gray-50 dark:bg-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-base font-semibold text-gray-900 dark:text-white">{getTypeLabel(groupKey)}</span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200">{items.length}</span>
                    </div>
                    <span className={`transform transition-transform text-gray-600 dark:text-gray-300 ${isOpen ? 'rotate-180' : ''}`}>⌄</span>
                  </button>

                  {isOpen && (
                    <div className="px-5 pb-5 pt-2">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {items.map((rule) => (
                          <div key={rule.rule_id} className="border border-gray-200 dark:border-gray-700 rounded-md p-4 hover:shadow-sm transition-shadow">
                            <div className="flex items-start justify-between">
                              <div className="min-w-0 pr-4">
                                <div className="text-sm text-gray-800 dark:text-gray-200 break-all">{rule.description || 'Custom rule'}</div>
                              </div>
                              <div className="flex items-center space-x-2 shrink-0">
                                <Badge variant={rule.action || 'default'}>{rule.action}</Badge>
                                <Badge severity={rule.severity}>{rule.severity}</Badge>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
    </div>
  );
}

