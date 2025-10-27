import { useState } from 'react';
import { useRouter } from 'next/router';
import toast from 'react-hot-toast';
import { setSession } from '../lib/session';

export default function Login() {
  const router = useRouter();
  const [showForm, setShowForm] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
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
        // Show specific error message from backend
        const errorMessage = errorData.detail || 'Login failed. Please try again.';
        
        // Check if it's a tenant not found or password mismatch
        if (errorMessage.toLowerCase().includes('tenant not found')) {
          throw new Error('Tenant not found. Please check the tenant name or create a new tenant.');
        } else if (errorMessage.toLowerCase().includes('invalid password')) {
          throw new Error('Invalid password. Please check your password and try again.');
        } else {
          throw new Error(errorMessage);
        }
      }
      
      const data = await response.json();
      
      // Store credentials with 1-hour timeout
      setSession(data.tenant_id, data.api_key, data.name);
      
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
      
      // Store credentials with 1-hour timeout
      setSession(data.tenant_id, data.api_key, data.name);
      
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
          <div className="card form-transition animate-fade-in">
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
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="input-field pr-10"
                    placeholder="Enter password"
                    aria-required="true"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none"
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.36m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
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
          <div className="card form-transition animate-fade-in">
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
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="input-field pr-10"
                    placeholder="Enter secure password (min 8 characters)"
                    aria-required="true"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none"
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.36m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
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
