import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const tenantId = sessionStorage.getItem('tenant_id');
    const apiKey = sessionStorage.getItem('api_key');
    
    if (!tenantId || !apiKey) {
      // Not logged in, redirect to login page
      router.push('/login');
    } else {
      // Logged in, redirect to test page
      router.push('/test');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="spinner mx-auto mb-4"></div>
        <p className="text-gray-600">Redirecting...</p>
      </div>
    </div>
  );
}
