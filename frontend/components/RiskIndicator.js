export default function RiskIndicator({ risk }) {
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'risk-critical';
      case 'high': return 'risk-high';
      case 'medium': return 'risk-medium';
      case 'low': return 'risk-low';
      default: return 'risk-low';
    }
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
      
      {risk.position && (
        <div className="mt-2 text-xs opacity-75">
          Position: {risk.position.start}-{risk.position.end}
        </div>
      )}
    </div>
  );
}
