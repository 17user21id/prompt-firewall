import { useSession } from 'next-auth/react';
import { useState, useEffect, useMemo } from 'react';
import { TYPE_LABELS } from '../../lib/constants';
import RuleEditor from '../../components/RuleEditor';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function Rules() {
  const { data: session, status } = useSession();
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingRule, setEditingRule] = useState(null);
  const [openGroups, setOpenGroups] = useState({});

  useEffect(() => {
    if (session) {
      fetchRules();
    }
  }, [session]);

  const fetchRules = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/rules`, {
        headers: { 
          'Authorization': `Bearer ${session.user.tenant_id}:${session.user.api_key}` 
        },
      });
      
      if (res.ok) {
        const data = await res.json();
        setRules(Array.isArray(data) ? data : []);
      } else {
        toast.error('Failed to fetch rules');
      }
    } catch (error) {
      toast.error('Error fetching rules');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async (ruleData) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/rules`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.user.tenant_id}:${session.user.api_key}`,
        },
        body: JSON.stringify(ruleData),
      });
      
      if (res.ok) {
        const newRule = await res.json();
        setRules(prev => [...prev, newRule]);
        toast.success('Rule created successfully');
      } else {
        const errorData = await res.json();
        toast.error(errorData.detail || 'Failed to create rule');
      }
    } catch (error) {
      toast.error('Error creating rule');
    }
  };

  const handleUpdateRule = async (ruleData) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/rules/${editingRule.rule_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.user.tenant_id}:${session.user.api_key}`,
        },
        body: JSON.stringify(ruleData),
      });
      
      if (res.ok) {
        const updatedRule = await res.json();
        setRules(prev => prev.map(rule => 
          rule.rule_id === editingRule.rule_id ? updatedRule : rule
        ));
        setEditingRule(null);
        toast.success('Rule updated successfully');
      } else {
        const errorData = await res.json();
        toast.error(errorData.detail || 'Failed to update rule');
      }
    } catch (error) {
      toast.error('Error updating rule');
    }
  };

  const handleDeleteRule = async (ruleId) => {
    if (!confirm('Are you sure you want to delete this rule?')) {
      return;
    }

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/rules/${ruleId}`, {
        method: 'DELETE',
        headers: { 
          'Authorization': `Bearer ${session.user.tenant_id}:${session.user.api_key}`
        },
      });
      
      if (res.ok) {
        setRules(prev => prev.filter(rule => rule.rule_id !== ruleId));
        toast.success('Rule deleted successfully');
      } else {
        toast.error('Failed to delete rule');
      }
    } catch (error) {
      toast.error('Error deleting rule');
    }
  };

  const getTypeLabel = (type) => TYPE_LABELS[type] || type;

  const getSeverityBadge = (severity) => {
    const severityClasses = {
      critical: 'badge-error',
      high: 'badge-warning',
      medium: 'badge-info',
      low: 'badge-success'
    };
    
    return (
      <span className={`badge ${severityClasses[severity] || 'badge-info'}`}>
        {severity}
      </span>
    );
  };

  // Group rules by type for UI without changing API
  const groupedRules = useMemo(() => {
    const groups = rules.reduce((acc, rule) => {
      const key = rule.type || 'OTHER';
      if (!acc[key]) acc[key] = [];
      acc[key].push(rule);
      return acc;
    }, {});
    return groups;
  }, [rules]);

  const toggleGroup = (group) => {
    setOpenGroups((prev) => ({ ...prev, [group]: !prev[group] }));
  };

  const getActionBadge = (action) => {
    const actionClasses = {
      block: 'badge-error',
      redact: 'badge-warning',
      warn: 'badge-info',
      allow: 'badge-success'
    };
    
    return (
      <span className={`badge ${actionClasses[action] || 'badge-info'}`}>
        {action}
      </span>
    );
  };

  if (status === 'loading' || loading) {
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
    <div className="container animate-fade-in">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Manage Rules</h1>
            <p className="text-gray-600 mt-2">Configure detection rules for PII and injection patterns</p>
          </div>
          <Link href="/admin" className="btn-secondary">
            ← Back to Dashboard
          </Link>
        </div>

        {/* Rule Editor */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {editingRule ? 'Edit Rule' : 'Create New Rule'}
          </h2>
          <RuleEditor 
            rule={editingRule}
            onSubmit={editingRule ? handleUpdateRule : handleCreateRule}
            onCancel={editingRule ? () => setEditingRule(null) : null}
          />
        </div>

        {/* Active Rules - Grouped by Type */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Active Rules</h2>

          {rules.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">⚙️</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No rules found</h3>
              <p className="text-gray-600">Create your first rule using the form above.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {Object.keys(groupedRules).sort().map((groupKey) => {
                const items = groupedRules[groupKey];
                const open = openGroups[groupKey] ?? true;
                return (
                  <div key={groupKey} className="border border-gray-200 rounded-lg overflow-hidden">
                    <button
                      onClick={() => toggleGroup(groupKey)}
                      className="w-full flex items-center justify-between px-5 py-4 bg-gray-50 hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <span className="text-lg font-semibold text-gray-900">{getTypeLabel(groupKey)}</span>
                        <span className="badge badge-neutral">{items.length}</span>
                      </div>
                      <span className={`transform transition-transform ${open ? 'rotate-180' : ''}`}>⌄</span>
                    </button>

                    {open && (
                      <div className="px-5 pb-5 pt-2 bg-white">
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {items.map((rule) => (
                                <tr key={rule.rule_id} className="hover:bg-gray-50">
                                  <td className="px-4 py-3 align-top">
                                    <div className="text-sm text-gray-800">
                                      {rule.description || 'Custom rule'}
                                    </div>
                                  </td>
                                  <td className="px-4 py-3 whitespace-nowrap">{getActionBadge(rule.action)}</td>
                                  <td className="px-4 py-3 whitespace-nowrap">{getSeverityBadge(rule.severity)}</td>
                                  <td className="px-4 py-3 whitespace-nowrap">
                                    <span className={`badge ${rule.enabled ? 'badge-success' : 'badge-error'}`}>
                                      {rule.enabled ? 'Enabled' : 'Disabled'}
                                    </span>
                                  </td>
                                  <td className="px-4 py-3 whitespace-nowrap">
                                    <div className="text-sm text-gray-500">v{rule.version || 1}</div>
                                  </td>
                                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium space-x-3">
                                    <button
                                      onClick={() => setEditingRule(rule)}
                                      className="text-primary-600 hover:text-primary-900 transition-colors duration-200"
                                    >
                                      Edit
                                    </button>
                                    <button
                                      onClick={() => handleDeleteRule(rule.rule_id)}
                                      className="text-red-600 hover:text-red-900 transition-colors duration-200"
                                    >
                                      Delete
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
