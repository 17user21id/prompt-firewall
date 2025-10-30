import { useState } from 'react';
import toast from 'react-hot-toast';
import { VALIDATION_MESSAGES } from '../lib/constants';

export default function PromptForm({ onSubmit }) {
  const MAX_PROMPT_LEN = 100000;
  const [formData, setFormData] = useState({
    tenantName: '',
    password: '',
    prompt: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.prompt.trim()) {
      toast.error(VALIDATION_MESSAGES.PROMPT_REQUIRED);
      return;
    }
    if (formData.prompt.length > 100000) {
      toast.error('Prompt too long. Maximum allowed is 100,000 characters.');
      return;
    }
    
    if (!formData.tenantName || !formData.password) {
      toast.error(VALIDATION_MESSAGES.TENANT_NAME_REQUIRED);
      return;
    }
    
    setLoading(true);
    try {
      await onSubmit(formData);
      setFormData(prev => ({ ...prev, prompt: '' }));
    } catch (error) {
      toast.error(error.message || 'Error processing prompt');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    if (field === 'prompt') {
      if (value.length > MAX_PROMPT_LEN) {
        toast.error('Prompt too long. Maximum allowed is 100,000 characters.');
        return;
      }
    }
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="card">
      <form onSubmit={handleSubmit} className="space-y-6" aria-label="Prompt Submission Form">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="tenantName" className="form-label">
              Tenant Name
            </label>
            <input
              id="tenantName"
              type="text"
              value={formData.tenantName}
              onChange={(e) => handleInputChange('tenantName', e.target.value)}
              className="input-field"
              placeholder="Enter your tenant name"
              aria-required="true"
              disabled={loading}
            />
          </div>
          
          <div>
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              className="input-field"
              placeholder="Enter your password"
              aria-required="true"
              disabled={loading}
            />
          </div>
        </div>
        
        <div>
          <label htmlFor="prompt" className="form-label">
            Prompt
          </label>
          <textarea
            id="prompt"
            value={formData.prompt}
            onChange={(e) => handleInputChange('prompt', e.target.value)}
            className="input-field resize-none text-base md:text-lg"
            rows={6}
            placeholder="Enter your prompt here... (e.g., 'Contact me at john@example.com for more information')"
            aria-required="true"
            disabled={loading}
            maxLength={MAX_PROMPT_LEN}
          />
          <div className="flex items-center justify-between mt-1">
            <p className="text-sm text-gray-500">
              Try entering prompts with PII (emails, phone numbers, SSNs) or injection attempts to see the firewall in action.
            </p>
            <p className={`text-xs ${formData.prompt.length >= MAX_PROMPT_LEN ? 'text-red-600' : 'text-gray-500'}`}>
              {formData.prompt.length}/{MAX_PROMPT_LEN}{formData.prompt.length >= MAX_PROMPT_LEN ? ' (maximum reached)' : ''}
            </p>
          </div>
        </div>
        
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Submit Prompt"
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                <span>Processing...</span>
              </>
            ) : (
              <span>Analyze Prompt</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
