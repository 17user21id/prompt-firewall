import { useState, useEffect } from 'react';
import TenantForm from '../../components/TenantForm';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function Tenants() {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchTenants();
  }, []);

  const fetchTenants = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/tenants');
      
      if (res.ok) {
        const data = await res.json();
        setTenants(Array.isArray(data) ? data : []);
      } else {
        const errorData = await res.json();
        toast.error(errorData.detail || 'Failed to fetch tenants');
      }
    } catch (error) {
      console.error('Error fetching tenants:', error);
      toast.error('Error fetching tenants');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTenant = async ({ name, password }) => {
    try {
      const res = await fetch('/api/tenants', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, password, metadata: {} }),
      });
      
      if (res.ok) {
        const newTenant = await res.json();
        setTenants(prev => [...prev, newTenant]);
        setShowForm(false);
        toast.success('Tenant created successfully! You can now use it for prompt testing.');
      } else {
        const errorData = await res.json();
        toast.error(errorData.detail || 'Failed to create tenant');
      }
    } catch (error) {
      console.error('Error creating tenant:', error);
      toast.error('Error creating tenant');
    }
  };

  if (loading) {
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

  return (
    <div className="container">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Manage Tenants</h1>
            <p className="text-gray-600 mt-2">Create tenant accounts for prompt testing</p>
          </div>
          <Link href="/" className="btn-secondary">
            ← Back to Home
          </Link>
        </div>

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

        {!showForm && (
          <div className="mb-8">
            <button 
              onClick={() => setShowForm(true)}
              className="btn-primary"
            >
              + Create New Tenant
            </button>
          </div>
        )}

        {/* Tenants List */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Existing Tenants</h2>
          
          {tenants.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">👥</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No tenants found</h3>
              <p className="text-gray-600">Create your first tenant using the form above.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tenant Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tenant ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      API Key
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {tenants.map((tenant) => (
                    <tr key={tenant.tenant_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {tenant.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-mono text-gray-500">
                          {tenant.tenant_id.slice(0, 8)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-mono text-gray-500">
                          {tenant.api_key ? tenant.api_key.slice(0, 8) + '...' : 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {tenant.created_at ? new Date(tenant.created_at).toLocaleDateString() : 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <span className="text-gray-400">View Only</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
