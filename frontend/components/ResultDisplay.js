import RiskIndicator from './RiskIndicator';
import { DECISION_ICONS } from '../lib/constants';
import { getDecisionColor, formatPercent } from '../lib/utils';

export default function ResultDisplay({ result }) {
  if (!result) return null;

  const getDecisionIcon = (decision) => {
    return DECISION_ICONS[decision] || DECISION_ICONS.info;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Decision Summary */}
      <div className={`card border-l-4 ${getDecisionColor(result.decision)}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{getDecisionIcon(result.decision)}</span>
            <div>
              <h3 className="text-lg font-semibold">
                Decision: {result.decision.toUpperCase()}
              </h3>
              {result.explanation && (
                <p className="text-sm mt-1">{result.explanation}</p>
              )}
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium">
              Confidence: {formatPercent(result.confidence)}%
            </div>
            {result.processing_time && (
              <div className="text-xs text-gray-500">
                Processed in {result.processing_time}ms
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modified Prompt */}
      {result.promptModified && result.promptModified !== result.prompt && (
        <div className="card">
          <h4 className="font-medium text-gray-700 mb-3">Modified Prompt:</h4>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 whitespace-pre-wrap font-mono">
              {result.promptModified}
            </p>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Sensitive information has been redacted or modified for security.
          </p>
        </div>
      )}

      {/* Risk Indicators */}
      {result.risks && result.risks.length > 0 && (
        <div className="card">
          <h4 className="font-medium text-gray-700 mb-4">Detected Risks:</h4>
          <div className="grid gap-3">
            {result.risks.map((risk, index) => (
              <RiskIndicator 
                key={index} 
                risk={risk} 
                originalPrompt={result.prompt || result.metadata?.prompt || ''} 
              />
            ))}
          </div>
        </div>
      )}

      {/* Anomaly Score */}
      {typeof result.anomaly_score === 'number' && (
        <div className="card">
          <h4 className="font-medium text-gray-700 mb-3">Risk Assessment:</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Anomaly Score</span>
              <span className="text-sm font-mono">
                {Math.round(result.anomaly_score * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  result.anomaly_score > 0.8 ? 'bg-red-500' :
                  result.anomaly_score > 0.6 ? 'bg-orange-500' :
                  result.anomaly_score > 0.4 ? 'bg-yellow-500' :
                  'bg-green-500'
                }`}
                style={{ width: `${result.anomaly_score * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-500">
              Higher scores indicate increased risk of security issues.
            </p>
          </div>
        </div>
      )}

      {/* Additional Information */}
      {(result.metadata || result.timestamp) && (
        <div className="card">
          <h4 className="font-medium text-gray-700 mb-3">Additional Information:</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            {result.timestamp && (
              <div>
                <span className="font-medium text-gray-600">Processed:</span>
                <span className="ml-2 text-gray-500">
                  {new Date(result.timestamp).toLocaleString()}
                </span>
              </div>
            )}
            {result.metadata?.model && (
              <div>
                <span className="font-medium text-gray-600">Model:</span>
                <span className="ml-2 text-gray-500">{result.metadata.model}</span>
              </div>
            )}
            {result.metadata?.version && (
              <div>
                <span className="font-medium text-gray-600">Version:</span>
                <span className="ml-2 text-gray-500">{result.metadata.version}</span>
              </div>
            )}
            {result.metadata?.tenant_id && (
              <div>
                <span className="font-medium text-gray-600">Tenant:</span>
                <span className="ml-2 text-gray-500 font-mono">
                  {result.metadata.tenant_id.slice(0, 8)}...
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
