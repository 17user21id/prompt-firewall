export default function RiskIndicator({ risk, originalPrompt = '' }) {
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'risk-critical';
      case 'high': return 'risk-high';
      case 'medium': return 'risk-medium';
      case 'low': return 'risk-low';
      default: return 'risk-low';
    }
  };

  const getSurroundingContext = () => {
    if (!originalPrompt || (risk.start === undefined && !risk.match)) {
      return null;
    }

    const matchText = risk.match || '';
    const windowSize = 30; // Characters before and after
    
    if (risk.start !== undefined && risk.end !== undefined) {
      const start = Math.max(0, risk.start - windowSize);
      const end = Math.min(originalPrompt.length, risk.end + windowSize);
      const beforeContext = originalPrompt.substring(start, risk.start);
      const matchText_actual = originalPrompt.substring(risk.start, risk.end);
      const afterContext = originalPrompt.substring(risk.end, end);
      
      return {
        before: beforeContext,
        match: matchText_actual,
        after: afterContext
      };
    }
    
    return null;
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'block': return '🚫';
      case 'redact': return '🔒';
      case 'warn': return '⚠️';
      case 'allow': return '✅';
      default: return 'ℹ️';
    }
  };

  const getTypeLabel = (type) => {
    const typeLabels = {
      'PII_EMAIL': 'Email Address',
      'PII_SSN': 'Social Security Number',
      'PII_PHONE': 'Phone Number',
      'PII_CREDIT_CARD': 'Credit Card',
      'PII_IP_ADDRESS': 'IP Address',
      'PII_URL': 'URL',
      'PII_MEDICAL_RECORD': 'Medical Record',
      'INJECTION': 'Prompt Injection',
      'INJECTION_OPENAI': 'OpenAI Injection',
      'CUSTOM': 'Custom Pattern'
    };
    return typeLabels[type] || type;
  };

  const context = getSurroundingContext();

  return (
    <div className={`risk-indicator ${getSeverityColor(risk.severity)}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-lg">{getActionIcon(risk.action)}</span>
          <div>
            <div className="font-medium">{getTypeLabel(risk.type)}</div>
            <div className="text-sm opacity-75 font-mono">
              {risk.match || 'Pattern matched'}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium capitalize">
            {risk.severity || 'Unknown'}
          </div>
          <div className="text-xs opacity-75">
            {Math.round((risk.confidence || 0.95) * 100)}% confidence
          </div>
        </div>
      </div>
      
      {risk.description && (
        <div className="mt-2 text-sm opacity-90">
          {risk.description}
        </div>
      )}
      
      {context && (
        <div className="mt-3 bg-gray-100 dark:bg-gray-700 p-3 rounded text-xs font-mono">
          <span className="text-gray-500 dark:text-gray-400">{context.before}</span>
          <span className="bg-red-200 dark:bg-red-900/50 text-red-800 dark:text-red-300 font-bold px-1 rounded">
            {context.match}
          </span>
          <span className="text-gray-500 dark:text-gray-400">{context.after}</span>
        </div>
      )}
      
      {risk.position && (
        <div className="mt-2 text-xs opacity-75">
          Position: {risk.position.start}-{risk.position.end}
        </div>
      )}
    </div>
  );
}
