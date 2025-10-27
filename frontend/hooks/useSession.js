import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { getSession, clearSession } from '../lib/session';
import toast from 'react-hot-toast';
import { ERROR_MESSAGES, INFO_MESSAGES, SUCCESS_MESSAGES } from '../lib/constants';

/**
 * Custom hook for session management
 */
export function useSession() {
  const router = useRouter();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = () => {
      const userSession = getSession();
      setSession(userSession);
      setLoading(false);
    };

    checkSession();
    // Check periodically in case session changes
    const interval = setInterval(checkSession, 1000);
    return () => clearInterval(interval);
  }, []);

  const logout = () => {
    clearSession();
    setSession(null);
    toast.success(SUCCESS_MESSAGES.LOGOUT_SUCCESS);
    router.push('/login');
  };

  const requireAuth = () => {
    if (!session) {
      toast.error(ERROR_MESSAGES.SESSION_EXPIRED);
      router.push('/login');
      return false;
    }
    return true;
  };

  return { session, loading, logout, requireAuth };
}

/**
 * Hook for API calls with loading state
 */
export function useApiCall() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const callApi = async (apiFunction, ...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiFunction(...args);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, callApi };
}

