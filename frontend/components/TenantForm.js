import { useState } from 'react';
import toast from 'react-hot-toast';

export default function TenantForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.password.trim()) {
      toast.error('Please fill all fields');
      return;
    }
    
    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters long');
      return;
    }
    
    setLoading(true);
    try {
      await onSubmit(formData);
      setFormData({ name: '', password: '' });
    } catch (error) {
      toast.error('Error creating tenant');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="card">
      <form onSubmit={handleSubmit} className="space-y-6" aria-label="Tenant Creation Form">
        <div>
          <label htmlFor="name" className="form-label">
            Tenant Name
          </label>
          <input
            id="name"
            type="text"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            className="input-field"
            placeholder="Enter tenant name (e.g., Acme Corp)"
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
            placeholder="Enter secure password (min 8 characters)"
            aria-required="true"
            disabled={loading}
          />
          <p className="text-sm text-gray-500 mt-1">
            Password must be at least 8 characters long and will be securely hashed.
          </p>
        </div>
        
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Create Tenant"
          >
            {loading ? (
              <>
                <div className="spinner"></div>
                <span>Creating...</span>
              </>
            ) : (
              <span>Create Tenant</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
