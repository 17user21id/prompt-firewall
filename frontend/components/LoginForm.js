import { useState } from 'react';
import toast from 'react-hot-toast';
import { signIn } from 'next-auth/react';

export default function LoginForm() {
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
    
    setLoading(true);
    try {
      const result = await signIn('credentials', {
        redirect: false,
        name: formData.name,
        password: formData.password,
      });
      
      if (result.error) {
        toast.error('Login failed. Please check your credentials.');
      } else {
        toast.success('Login successful! Redirecting to admin console...');
      }
    } catch (error) {
      toast.error('Error logging in');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="card max-w-md mx-auto">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Admin Login</h2>
        <p className="text-gray-600 mt-2">Sign in to access the admin console</p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6" aria-label="Tenant Login Form">
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
            onChange={(e) => handleInputChange('password', e.target.value)}
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
        <p className="text-sm text-gray-600">
          Don't have a tenant? 
          <a href="/admin/tenants" className="text-primary-600 hover:text-primary-700 ml-1 font-medium">
            Create one here
          </a>
        </p>
      </div>
    </div>
  );
}
