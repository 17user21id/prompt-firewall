import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { getSession } from '../lib/session';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in and session is valid
    const session = getSession();
    
    if (!session) {
      // Session expired or not logged in, redirect to login page
      router.push('/login');
    } else {
      // Logged in, redirect to test page
      router.push('/test');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors duration-300 animate-fade-in">
      <div className="text-center">
        <div className="spinner mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-300">Redirecting...</p>
      </div>
    </div>
  );
}
