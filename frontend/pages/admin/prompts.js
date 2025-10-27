import { useSession } from 'next-auth/react';
import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function Prompts() {
  const { data: session, status } = useSession();
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    decision: '',
    riskType: '',
    hasRisks: null,
    dateFrom: '',
    dateTo: ''
  });

  useEffect(() => {
    if (session) {
      fetchPrompts();
    }
  }, [session, filters]);

  const fetchPrompts = async () => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams();
      if (filters.decision) queryParams.append('decision', filters.decision);
      if (filters.riskType) queryParams.append('risk_type', filters.riskType);
      if (filters.hasRisks !== null) queryParams.append('has_risks', filters.hasRisks);
      if (filters.dateFrom) queryParams.append('date_from', filters.dateFrom);
      if (filters.dateTo) queryParams.append('date_to', filters.dateTo);
      
      const res = await fetch(`/api/prompts?${queryParams.toString()}`, {
        headers: { 
          'Authorization': `Bearer ${session.user.tenant_id}:${session.user.api_key}` 
        },
      });
      
      if (res.ok) {
        const data = await res.json();
        setPrompts(Array.isArray(data) ? data : []);
      } else {
        toast.error('Failed to fetch prompts');
      }
    } catch (error) {
      toast.error('Error fetching prompts');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      decision: '',
      riskType: '',
      hasRisks: null,
      dateFrom: '',
      dateTo: ''
    });
  };

  const getDecisionBadge = (decision) => {
    const classes = {
      'block': 'badge-error',
      'redact': 'badge-warning',
      'warn': 'badge-info',
      'allow': 'badge-success'
    };
    
    return (
      <span className={`badge ${classes[decision] || 'badge-info'}`}>
        {decision.toUpperCase()}
      </span>
    );
  };

  const getRiskTypeBadge = (type) => {
    const typeStr = type.toUpperCase();
    let className = 'badge-info';
    let label = type;
    
    if (typeStr.includes('PII')) {
      className = 'badge-warning';
      label = 'PII';
    } else if (typeStr.includes('CREDIT_CARD') || typeStr.includes('PCI')) {
      className = 'badge-error';
      label = 'PCI';
    } else if (typeStr.includes('MEDICAL') || typeStr.includes('PHI')) {
      className = 'badge-error';
      label = 'PHI';
    } else if (typeStr.includes('INJECTION')) {
      className = 'badge-error';
      label = 'INJECTION';
    }
    
    return (
      <span className={`badge ${className}`}>
        {label}
      </span>
    );
  };

  const getRiskTypeLabel = (type) => {
    const typeStr = type.toUpperCase();
    
    if (typeStr.includes('EMAIL')) return 'Email';
    if (typeStr.includes('SSN')) return 'SSN';
    if (typeStr.includes('PHONE')) return 'Phone';
    if (typeStr.includes('CREDIT_CARD')) return 'Credit Card';
    if (typeStr.includes('IP_ADDRESS')) return 'IP Address';
    if (typeStr.includes('URL')) return 'URL';
    if (typeStr.includes('MEDICAL')) return 'Medical Record';
    if (typeStr.includes('INJECTION')) return 'Prompt Injection';
    
    return type.replace(/_/g, ' ');
  };

  if (status === 'loading' || loading) {
    return (
      <div className="container">
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center space-x-3">
            <div className="spinner"></div>
            <span className="text-gray-600 dark:text-gray-300">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="container">
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Access Denied</h1>
          <p className="text-gray-600 dark:text-gray-300 mb-6">Please log in to access the admin console.</p>
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
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Prompt History</h1>
            <p className="text-gray-600 dark:text-gray-300 mt-2">View and filter all processed prompts with risk details</p>
          </div>
          <Link href="/admin" className="btn-secondary">
            ← Back to Dashboard
          </Link>
        </div>

        {/* Filters */}
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="form-label">Decision</label>
              <select
                value={filters.decision}
                onChange={(e) => handleFilterChange('decision', e.target.value)}
                className="input-field"
              >
                <option value="">All Decisions</option>
                <option value="block">Block</option>
                <option value="redact">Redact</option>
                <option value="warn">Warn</option>
                <option value="allow">Allow</option>
              </select>
            </div>

            <div>
              <label className="form-label">Risk Type</label>
              <select
                value={filters.riskType}
                onChange={(e) => handleFilterChange('riskType', e.target.value)}
                className="input-field"
              >
                <option value="">All Risk Types</option>
                <option value="PII">PII (Personally Identifiable Information)</option>
                <option value="PCI">PCI (Credit Card Data)</option>
                <option value="PHI">PHI (Protected Health Information)</option>
                <option value="INJECTION">Prompt Injection</option>
              </select>
            </div>

            <div>
              <label className="form-label">Has Risks</label>
              <select
                value={filters.hasRisks === null ? '' : filters.hasRisks.toString()}
                onChange={(e) => handleFilterChange('hasRisks', e.target.value === '' ? null : e.target.value === 'true')}
                className="input-field"
              >
                <option value="">All</option>
                <option value="true">Has Risks</option>
                <option value="false">No Risks</option>
              </select>
            </div>

            <div>
              <label className="form-label">Date From</label>
              <input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                className="input-field"
              />
            </div>

            <div>
              <label className="form-label">Date To</label>
              <input
                type="date"
                value={filters.dateTo}
                onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                className="input-field"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={clearFilters}
                className="btn-secondary w-full"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Prompts List */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Prompts ({prompts.length})
          </h2>
          
          {prompts.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 dark:text-gray-500 text-6xl mb-4">📝</div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No prompts found</h3>
              <p className="text-gray-600 dark:text-gray-400">No prompts match the current filters.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {prompts.map((prompt) => (
                <div 
                  key={prompt.prompt_id} 
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center space-x-2 mb-2">
                        {getDecisionBadge(prompt.decision)}
                        {prompt.risks && prompt.risks.length > 0 && (
                          <span className="badge badge-warning">
                            {prompt.risks.length} Risk(s)
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(prompt.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Score: {(prompt.anomaly_score * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Confidence: {(prompt.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>

                  <div className="mb-3">
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1 block">
                      Original Prompt:
                    </label>
                    <p className="text-sm text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800 p-2 rounded">
                      {prompt.prompt}
                    </p>
                  </div>

                  {prompt.promptModified !== prompt.prompt && (
                    <div className="mb-3">
                      <label className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1 block">
                        Modified Prompt:
                      </label>
                      <p className="text-sm text-gray-900 dark:text-white bg-yellow-50 dark:bg-yellow-900/20 p-2 rounded">
                        {prompt.promptModified}
                      </p>
                    </div>
                  )}

                  {prompt.risks && prompt.risks.length > 0 && (
                    <div>
                      <label className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 block">
                        Detected Risks:
                      </label>
                      <div className="space-y-2">
                        {prompt.risks.map((risk, idx) => (
                          <div 
                            key={idx}
                            className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-2"
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-1">
                                  {getRiskTypeBadge(risk.type)}
                                  <span className="text-xs font-medium text-gray-900 dark:text-white">
                                    {getRiskTypeLabel(risk.type)}
                                  </span>
                                </div>
                                <p className="text-xs text-gray-600 dark:text-gray-300">
                                  Match: <span className="font-mono">{risk.match}</span>
                                </p>
                                {risk.reasoning && (
                                  <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">
                                    {risk.reasoning}
                                  </p>
                                )}
                              </div>
                              <div className="text-right">
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                  Confidence: {(risk.confidence * 100).toFixed(0)}%
                                </p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                  Severity: {risk.severity}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {prompt.reason && (
                    <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                      <label className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1 block">
                        Reason:
                      </label>
                      <p className="text-xs text-gray-600 dark:text-gray-300">
                        {prompt.reason}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

