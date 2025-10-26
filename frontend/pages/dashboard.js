import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import toast from 'react-hot-toast';
import Link from 'next/link';

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
    // Check if user is logged in
    const tenantId = sessionStorage.getItem('tenant_id');
    const apiKey = sessionStorage.getItem('api_key');
    const tenantName = sessionStorage.getItem('tenant_name');
    
    if (!tenantId || !apiKey) {
      router.push('/login');
      return;
    }
    
    setTenantInfo({ tenant_id: tenantId, api_key: apiKey, name: tenantName });
    loadData(tenantId, apiKey);
  }, []);

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
        setLogs(logsData.logs || []);
        calculateStats(logsData.logs || []);
      }
      
      // Load rules
      const rulesResponse = await fetch(`/api/rules?tenant_id=${tenantId}`, {
        headers: {
          'Authorization': `Bearer ${tenantId}:${apiKey}`
        }
      });
      
      if (rulesResponse.ok) {
        const rulesData = await rulesResponse.json();
        setRules(rulesData.rules || []);
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
      if (log.decision === 'block') {
        stats.blockedPrompts++;
      } else if (log.decision === 'redact') {
        stats.redactedPrompts++;
      } else {
        stats.allowedPrompts++;
      }
    });
    
    setStats(stats);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('tenant_id');
    sessionStorage.removeItem('api_key');
    sessionStorage.removeItem('tenant_name');
    router.push('/login');
  };

  if (loading || !tenantInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">
              Dashboard - {tenantInfo.name}
            </h1>
            <div className="flex items-center space-x-4">
              <Link href="/test" className="text-indigo-600 hover:text-indigo-800">
                Test Prompts
              </Link>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Total Prompts</div>
            <div className="mt-2 text-3xl font-semibold text-gray-900">{stats.totalPrompts}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-red-600">Blocked</div>
            <div className="mt-2 text-3xl font-semibold text-red-600">{stats.blockedPrompts}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-yellow-600">Redacted</div>
            <div className="mt-2 text-3xl font-semibold text-yellow-600">{stats.redactedPrompts}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-green-600">Allowed</div>
            <div className="mt-2 text-3xl font-semibold text-green-600">{stats.allowedPrompts}</div>
          </div>
        </div>

        {/* Logs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Prompts</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prompt
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Decision
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Risks
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs.slice(0, 10).map((log, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {log.prompt?.substring(0, 100)}...
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        log.decision === 'block' ? 'bg-red-100 text-red-800' :
                        log.decision === 'redact' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {log.decision}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {log.risks?.length || 0} risk(s)
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Rules */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Active Rules</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {rules.map((rule, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">{rule.type}</h3>
                      <p className="text-sm text-gray-600">{rule.description}</p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className={`px-3 py-1 text-xs rounded-full ${
                        rule.action === 'block' ? 'bg-red-100 text-red-800' :
                        rule.action === 'redact' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {rule.action}
                      </span>
                      <span className={`px-3 py-1 text-xs rounded-full ${
                        rule.severity === 'high' ? 'bg-red-100 text-red-800' :
                        rule.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
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
    </div>
  );
}

