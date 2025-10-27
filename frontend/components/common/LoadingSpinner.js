import { INFO_MESSAGES } from '../../lib/constants';

/**
 * Loading Spinner Component
 */
export default function LoadingSpinner({ message = INFO_MESSAGES.LOADING, size = 'default' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    default: 'w-5 h-5',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div className="flex items-center justify-center py-12">
      <div className="flex items-center space-x-3">
        <div className={`spinner ${sizeClasses[size] || sizeClasses.default}`} />
        {message && (
          <span className="text-gray-600 dark:text-gray-300">{message}</span>
        )}
      </div>
    </div>
  );
}

