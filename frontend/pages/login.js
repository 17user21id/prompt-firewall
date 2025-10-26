import { useState } from 'react';
import { useRouter } from 'next/router';
import toast from 'react-hot-toast';

export default function Login() {
  const router = useRouter();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.password.trim()) {
      toast.error('Please fill all fields');
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
          name: formData.name,
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

  const handleCreateTenant = async (e) => {
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
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/v1/tenants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          password: formData.password,
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
      router.push('/dashboard');
    } catch (error) {
      console.error('Error creating tenant:', error);
      toast.error(`Error creating tenant: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Prompt Firewall</h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            {!showForm ? 'Login to access your tenant' : 'Create a new tenant account'}
          </p>
        </div>

        {/* Login Form */}
        {!showForm && (
          <div className="card">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Login</h2>
              <p className="text-gray-600 dark:text-gray-300 mt-2">Sign in to your tenant account</p>
            </div>
            <form onSubmit={handleLogin} className="space-y-6" aria-label="Login Form">
              <div>
                <label htmlFor="name" className="form-label">
                  Tenant Name
                </label>
                <input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input-field"
                  placeholder="Enter tenant name"
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
                  placeholder="Enter password"
                  aria-required="true"
                  disabled={loading}
                />
              </div>
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Login"
                >
                  {loading ? (
                    <>
                      <div className="spinner"></div>
                      <span>Logging in...</span>
                    </>
                  ) : (
                    <span>Login</span>
                  )}
                </button>
              </div>
            </form>
            
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Don't have a tenant?{' '}
                <button
                  onClick={() => {
                    setShowForm(true);
                    setFormData({ name: '', password: '' });
                  }}
                  className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium"
                >
                  Create one here
                </button>
              </p>
            </div>
          </div>
        )}

        {/* Create Tenant Form */}
        {showForm && (
          <div className="card">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Create Tenant</h2>
              <p className="text-gray-600 dark:text-gray-300 mt-2">Register a new tenant account</p>
            </div>
            <form onSubmit={handleCreateTenant} className="space-y-6" aria-label="Tenant Creation Form">
              <div>
                <label htmlFor="name" className="form-label">
                  Tenant Name
                </label>
                <input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
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
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="input-field"
                  placeholder="Enter secure password (min 8 characters)"
                  aria-required="true"
                  disabled={loading}
                />
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Password must be at least 8 characters long and will be securely hashed.
                </p>
              </div>
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
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
            
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Already have a tenant?{' '}
                <button
                  onClick={() => {
                    setShowForm(false);
                    setFormData({ name: '', password: '' });
                  }}
                  className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium"
                >
                  Login here
                </button>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
