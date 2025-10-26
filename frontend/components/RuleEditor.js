import { useState } from 'react';
import toast from 'react-hot-toast';

export default function RuleEditor({ rule = null, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    type: rule?.type || 'PII_EMAIL',
    pattern: rule?.pattern || '',
    action: rule?.action || 'redact',
    severity: rule?.severity || 'high',
    enabled: rule?.enabled ?? true,
    description: rule?.description || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.pattern.trim()) {
      toast.error('Pattern is required');
      return;
    }
    
    if (!formData.description.trim()) {
      toast.error('Description is required');
      return;
    }
    
    setLoading(true);
    try {
      await onSubmit(formData);
      if (!rule) {
        setFormData({
          type: 'PII_EMAIL',
          pattern: '',
          action: 'redact',
          severity: 'high',
          enabled: true,
          description: ''
        });
      }
    } catch (error) {
      toast.error('Error saving rule');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const ruleTypes = [
    { value: 'PII_EMAIL', label: 'Email Address' },
    { value: 'PII_SSN', label: 'Social Security Number' },
    { value: 'PII_PHONE', label: 'Phone Number' },
    { value: 'PII_CREDIT_CARD', label: 'Credit Card' },
    { value: 'PII_IP_ADDRESS', label: 'IP Address' },
    { value: 'PII_URL', label: 'URL' },
    { value: 'PII_MEDICAL_RECORD', label: 'Medical Record' },
    { value: 'INJECTION', label: 'Prompt Injection' },
    { value: 'INJECTION_OPENAI', label: 'OpenAI Injection' },
    { value: 'CUSTOM', label: 'Custom Pattern' }
  ];

  const actions = [
    { value: 'block', label: 'Block', description: 'Completely block the request' },
    { value: 'redact', label: 'Redact', description: 'Remove sensitive information' },
    { value: 'warn', label: 'Warn', description: 'Allow but log warning' },
    { value: 'allow', label: 'Allow', description: 'Allow without modification' }
  ];

  const severities = [
    { value: 'critical', label: 'Critical', color: 'text-red-600' },
    { value: 'high', label: 'High', color: 'text-orange-600' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-600' },
    { value: 'low', label: 'Low', color: 'text-blue-600' }
  ];

  return (
    <div className="card">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          {rule ? 'Edit Rule' : 'Create New Rule'}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Configure detection rules for PII and prompt injection attempts.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6" aria-label="Rule Editor Form">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="type" className="form-label">
              Rule Type
            </label>
            <select
              id="type"
              value={formData.type}
              onChange={(e) => handleInputChange('type', e.target.value)}
              className="input-field"
              aria-required="true"
              disabled={loading}
            >
              {ruleTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="action" className="form-label">
              Action
            </label>
            <select
              id="action"
              value={formData.action}
              onChange={(e) => handleInputChange('action', e.target.value)}
              className="input-field"
              aria-required="true"
              disabled={loading}
            >
              {actions.map(action => (
                <option key={action.value} value={action.value}>
                  {action.label} - {action.description}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="pattern" className="form-label">
            Pattern (Regex)
          </label>
          <input
            id="pattern"
            type="text"
            value={formData.pattern}
            onChange={(e) => handleInputChange('pattern', e.target.value)}
            className="input-field font-mono"
            placeholder="Enter regex pattern (e.g., [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
            aria-required="true"
            disabled={loading}
          />
          <p className="text-sm text-gray-500 mt-1">
            Use regex patterns to match sensitive data. Test your pattern before saving.
          </p>
        </div>

        <div>
          <label htmlFor="description" className="form-label">
            Description
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            className="input-field resize-none"
            rows={3}
            placeholder="Describe what this rule detects and why it's important"
            aria-required="true"
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="severity" className="form-label">
              Severity Level
            </label>
            <select
              id="severity"
              value={formData.severity}
              onChange={(e) => handleInputChange('severity', e.target.value)}
              className="input-field"
              aria-required="true"
              disabled={loading}
            >
              {severities.map(severity => (
                <option key={severity.value} value={severity.value}>
                  {severity.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="enabled"
              checked={formData.enabled}
              onChange={(e) => handleInputChange('enabled', e.target.checked)}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              disabled={loading}
            />
            <label htmlFor="enabled" className="text-sm font-medium text-gray-700">
              Enable this rule
            </label>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="btn-secondary"
              disabled={loading}
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label={rule ? 'Update Rule' : 'Create Rule'}
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                <span>{rule ? 'Updating...' : 'Creating...'}</span>
              </>
            ) : (
              <span>{rule ? 'Update Rule' : 'Create Rule'}</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
