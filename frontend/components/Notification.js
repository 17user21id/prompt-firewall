import { Toaster } from 'react-hot-toast';
import { TOAST_CONFIG } from '../lib/constants';

export default function Notification() {
  return (
    <Toaster
      position={TOAST_CONFIG.position}
      toastOptions={{
        duration: TOAST_CONFIG.duration,
        style: TOAST_CONFIG.style,
        success: TOAST_CONFIG.success,
        error: TOAST_CONFIG.error,
        loading: TOAST_CONFIG.loading,
      }}
    />
  );
}
