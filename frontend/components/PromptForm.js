import { useState } from 'react';
import toast from 'react-hot-toast';

export default function PromptForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    tenantName: '',
    password: '',
    prompt: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }
    
    if (!formData.tenantName || !formData.password) {
      toast.error('Please provide tenant name and password');
      return;
    }
    
    setLoading(true);
    try {
      await onSubmit(formData);
      setFormData(prev => ({ ...prev, prompt: '' }));
    } catch (error) {
      toast.error('Error processing prompt');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
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
            className="input-field resize-none"
            rows={6}
            placeholder="Enter your prompt here... (e.g., 'Contact me at john@example.com for more information')"
            aria-required="true"
            disabled={loading}
          />
          <p className="text-sm text-gray-500 mt-1">
            Try entering prompts with PII (emails, phone numbers, SSNs) or injection attempts to see the firewall in action.
          </p>
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
