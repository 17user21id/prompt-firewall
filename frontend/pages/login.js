import { useState } from 'react';
import { useRouter } from 'next/router';
import toast from 'react-hot-toast';
import TenantForm from '../components/TenantForm';

export default function Login() {
  const router = useRouter();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    tenantName: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    
    if (!formData.tenantName || !formData.password) {
      toast.error('Please enter tenant name and password');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/v1/tenants/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.tenantName,
          password: formData.password,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const data = await response.json();
      
      // Store credentials in sessionStorage
      sessionStorage.setItem('tenant_id', data.tenant_id);
      sessionStorage.setItem('api_key', data.api_key);
      sessionStorage.setItem('tenant_name', data.name);
      
      toast.success('Login successful!');
      router.push('/dashboard');
    } catch (error) {
      console.error('Error logging in:', error);
      toast.error(`Login failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTenant = async ({ name, password }) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/v1/tenants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name,
          password: password,
          metadata: {}
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create tenant');
      }
      
      const data = await response.json();
      
      // Store credentials in sessionStorage
      sessionStorage.setItem('tenant_id', data.tenant_id);
      sessionStorage.setItem('api_key', data.api_key);
      sessionStorage.setItem('tenant_name', data.name);
      
      toast.success('Tenant created successfully!');
      setShowForm(false);
      router.push('/dashboard');
    } catch (error) {
      console.error('Error creating tenant:', error);
      toast.error(`Error creating tenant: ${error.message}`);
    }
  };

  return (
    <div className="container">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Prompt Firewall</h1>
            <p className="text-gray-600 mt-2">Login or create a tenant account to test prompts</p>
          </div>
        </div>

        {/* Login Form */}
        {!showForm && (
          <div className="card mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Login</h2>
            <form onSubmit={handleLogin} className="space-y-6" aria-label="Login Form">
              <div>
                <label htmlFor="tenantName" className="form-label">
                  Tenant Name
                </label>
                <input
                  id="tenantName"
                  type="text"
                  value={formData.tenantName}
                  onChange={(e) => setFormData({ ...formData, tenantName: e.target.value })}
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
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="input-field"
                  placeholder="Enter your password"
                  aria-required="true"
                  disabled={loading}
                />
              </div>
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Sign In"
                >
                  {loading ? (
                    <>
                      <div className="spinner"></div>
                      <span>Signing in...</span>
                    </>
                  ) : (
                    <span>Sign In</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Create Tenant Form */}
        {showForm && (
          <div className="mb-8 card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Create New Tenant</h2>
            <TenantForm onSubmit={handleCreateTenant} />
            <button 
              onClick={() => setShowForm(false)}
              className="btn-secondary mt-4"
            >
              Cancel
            </button>
          </div>
        )}

        {/* Toggle between Login and Create */}
        {!showForm ? (
          <div className="mb-8 text-center">
            <p className="text-gray-600 mb-4">Don't have an account?</p>
            <button 
              onClick={() => setShowForm(true)}
              className="btn-primary"
            >
              + Create New Tenant Account
            </button>
          </div>
        ) : (
          <div className="mb-8 text-center">
            <p className="text-gray-600 mb-4">Already have an account?</p>
            <button 
              onClick={() => setShowForm(false)}
              className="btn-secondary"
            >
              ← Back to Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
