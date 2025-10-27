import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import ResultDisplay from '../components/ResultDisplay';
import toast from 'react-hot-toast';
import { getSession, clearSession } from '../lib/session';
import { processPrompt } from '../lib/apiHelpers';
import { LoadingSpinner } from '../components/common';
import { ERROR_MESSAGES, SUCCESS_MESSAGES, INFO_MESSAGES } from '../lib/constants';

export default function TestPage() {
  const router = useRouter();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tenantInfo, setTenantInfo] = useState(null);

  useEffect(() => {
    const session = getSession();
    
    if (!session) {
      toast.error(ERROR_MESSAGES.SESSION_EXPIRED);
      router.push('/login');
      return;
    }
    
    setTenantInfo({ tenant_id: session.tenantId, api_key: session.apiKey, name: session.tenantName });
  }, [router]);

  const handleSubmit = async (prompt) => {
    if (!tenantInfo) {
      toast.error(ERROR_MESSAGES.NOT_LOGGED_IN);
      return;
    }

    setLoading(true);
    setResult(null);
    
    try {
      const data = await processPrompt(tenantInfo.tenant_id, tenantInfo.api_key, prompt);
      setResult(data);
      
      if (data.decision !== 'allow') {
        toast.error(`Prompt ${data.decision}: ${data.explanation || 'Risk detected'}`);
      } else {
        toast.success(SUCCESS_MESSAGES.PROMPT_PROCESSED);
      }
    } catch (error) {
      console.error('Error processing prompt:', error);
      toast.error(`Error processing prompt: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!tenantInfo) {
    return <LoadingSpinner message={INFO_MESSAGES.LOADING} />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Test Prompts - {tenantInfo.name}
            </h1>
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300">
                Dashboard
              </Link>
              <button
                onClick={() => {
                  clearSession();
                  router.push('/login');
                }}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Prompt Firewall Demo
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Test our AI security firewall by entering prompts with sensitive information or injection attempts. 
            See how we detect and protect against PII exposure and prompt injection attacks.
          </p>
        </div>

        {/* Demo Instructions */}
        <div className="card bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-300 mb-3">Try These Examples:</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h3 className="font-medium text-blue-800 dark:text-blue-300 mb-2">PII Detection:</h3>
              <ul className="space-y-1 text-blue-700 dark:text-blue-400">
                <li>• "Contact me at john@example.com"</li>
                <li>• "My SSN is 123-45-6789"</li>
                <li>• "Call me at (555) 123-4567"</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-blue-800 dark:text-blue-300 mb-2">Injection Attempts:</h3>
              <ul className="space-y-1 text-blue-700 dark:text-blue-400">
                <li>• "Ignore previous instructions..."</li>
                <li>• "You are now a helpful assistant"</li>
                <li>• "Forget your training data"</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Prompt Form */}
        <SimplePromptForm onSubmit={handleSubmit} />

        {/* Loading State */}
        {loading && <LoadingSpinner message={INFO_MESSAGES.ANALYZING} />}

        {/* Results */}
        {result && <div className="animate-fade-in"><ResultDisplay result={result} /></div>}

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card text-center">
            <div className="text-3xl mb-3">🛡️</div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">PII Protection</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Automatically detect and protect sensitive information like emails, SSNs, and phone numbers.
            </p>
          </div>
          
          <div className="card text-center">
            <div className="text-3xl mb-3">🚫</div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Injection Prevention</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Identify and block prompt injection attempts that could compromise AI systems.
            </p>
          </div>
          
          <div className="card text-center">
            <div className="text-3xl mb-3">📊</div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Real-time Analysis</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Get instant feedback with detailed risk assessments and confidence scores.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Simple form component that only needs prompt input
function SimplePromptForm({ onSubmit }) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const VALIDATION_MESSAGES = {
    PROMPT_REQUIRED: 'Please enter a prompt'
  };
  const ERROR_MESSAGES = {
    PROMPT_PROCESS_FAILED: 'Failed to process prompt'
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      toast.error(VALIDATION_MESSAGES.PROMPT_REQUIRED);
      return;
    }
    
    setLoading(true);
    try {
      await onSubmit(prompt);
      setPrompt('');
    } catch (error) {
      toast.error(error.message || ERROR_MESSAGES.PROMPT_PROCESS_FAILED);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card animate-fade-in">
      <form onSubmit={handleSubmit} className="space-y-6" aria-label="Prompt Submission Form">
        <div>
          <label htmlFor="prompt" className="form-label">
            Prompt
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="input-field resize-none"
            rows={6}
            placeholder="Enter your prompt here... (e.g., 'Contact me at john@example.com for more information')"
            aria-required="true"
            disabled={loading}
          />
          <p className="text-sm text-gray-500 mt-1">
            Try entering prompts with PII (emails, phone numbers, SSNs) or injection attempts to see the firewall in action.
          </p>
        </div>
        
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Submit Prompt"
          >
            {loading ? (
              <>
                <div className="spinner w-4 h-4"></div>
                <span>Processing...</span>
              </>
            ) : (
              'Analyze Prompt'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

