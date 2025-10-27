/**
 * Badge Component for displaying status indicators
 */
export default function Badge({ 
  children, 
  variant = 'default', 
  severity, 
  eventType,
  className = '' 
}) {
  // Get class based on variant
  const getVariantClass = () => {
    if (severity) {
      const severityClasses = {
        critical: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
        high: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300',
        medium: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
        low: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
      };
      return severityClasses[severity] || 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300';
    }
    
    if (eventType) {
      const eventClasses = {
        processed: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300',
        blocked: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
        redacted: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
        warned: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
        error: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
      };
      return eventClasses[eventType] || 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300';
    }

    const variants = {
      success: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      error: 'bg-red-100 text-red-800',
      info: 'bg-blue-100 text-blue-800',
      default: 'bg-gray-100 text-gray-800',
      // Action variants
      block: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
      redact: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
      warn: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
      allow: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
    };
    
    return variants[variant] || variants.default;
  };

  return (
    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getVariantClass()} ${className}`}>
      {children}
    </span>
  );
}

