import { useState, useMemo } from 'react';
import Badge from './common/Badge';
import { LoadingSpinner } from './common';
import { copyToClipboard, generateCSV } from '../lib/utils';
import { VALIDATION_MESSAGES } from '../lib/constants';

export default function LogTable({ logs = [], loading = false }) {
  const [filters, setFilters] = useState({
    eventType: '',
    severity: '',
    dateRange: '',
    riskCategories: [] // Changed to array for multi-select
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedLog, setSelectedLog] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const itemsPerPage = 20;

  // Helper functions defined before useMemo hooks that use them
  const getRiskCategoryBadges = (log) => {
    // Use risk_categories from API response if available
    if (log.risk_categories && Array.isArray(log.risk_categories)) {
      return log.risk_categories;
    }
    // Fallback to parsing from details.risks if not available
    const risks = log.details?.risks || [];
    const categories = new Set();
    risks.forEach(risk => {
      if (typeof risk === 'object' && risk !== null) {
        const category = risk.category || risk.type?.split('_')[0];
        if (category) categories.add(category);
      }
    });
    return Array.from(categories);
  };

  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      if (filters.eventType && log.event_type !== filters.eventType) return false;
      if (filters.severity && log.severity !== filters.severity) return false;
      if (filters.dateRange) {
        const logDate = new Date(log.timestamp);
        const filterDate = new Date(filters.dateRange);
        if (logDate < filterDate) return false;
      }
      if (filters.riskCategories.length > 0) {
        // Use risk_categories from API response if available, otherwise parse from details
        const logCategories = log.risk_categories || getRiskCategoryBadges(log);
        const hasMatchingCategory = logCategories.some(cat =>
          filters.riskCategories.includes(cat.toUpperCase())
        );
        if (!hasMatchingCategory) return false;
      }
      return true;
    });
  }, [logs, filters]);

  const paginatedLogs = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredLogs.slice(startIndex, endIndex);
  }, [filteredLogs, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(filteredLogs.length / itemsPerPage);

  const handleRowClick = (log) => {
    setSelectedLog(log);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedLog(null);
  };

  const handleCopyPrompt = async () => {
    const prompt = selectedLog?.details?.prompt || selectedLog?.metadata?.prompt;
    if (prompt) {
      const success = await copyToClipboard(prompt);
      if (success) {
        // Success message can be shown via toast
        console.log('Prompt copied to clipboard');
      }
    }
  };

  const handleExportLogs = () => {
    if (filteredLogs.length === 0) {
      console.log(VALIDATION_MESSAGES.NO_LOGS_TO_EXPORT);
      return;
    }

    const csvData = filteredLogs.map(log => ({
      log_id: log.log_id,
      prompt_id: log.prompt_id || 'N/A',
      event_type: log.event_type,
      severity: log.severity || 'N/A',
      details: JSON.stringify(log.details),
      timestamp: new Date(log.timestamp).toISOString()
    }));

    generateCSV(csvData, 'logs');
  };

  const getSeverityBadge = (severity) => {
    return <Badge severity={severity}>{severity || 'N/A'}</Badge>;
  };

  const getEventTypeBadge = (eventType) => {
    return <Badge eventType={eventType}>{eventType}</Badge>;
  };


  const formatReasons = (reasonString) => {
    if (!reasonString) return [];
    
    // New structured format: multiline with categories and matches
    if (reasonString.includes('\n')) {
      const lines = reasonString.split('\n').filter(line => line.trim());
      return lines.map(line => {
        // If line starts with category name, format it nicely
        if (line.includes(':')) {
          const [category, matches] = line.split(':').map(s => s.trim());
          return {
            category,
            matches
          };
        }
        return { text: line };
      });
    }
    
    // Fallback for old format: split by semicolons
    return reasonString.split(';').filter(r => r.trim()).map(r => ({ text: r }));
  };

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center space-x-3">
            <div className="spinner"></div>
            <span className="text-gray-600 dark:text-gray-300">Loading logs...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-6">
        {/* Filters - Order matches table columns */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex-1 min-w-48">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">From Date</label>
              <input
                type="date"
                value={filters.dateRange}
                onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div className="flex-1 min-w-48">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Event Type</label>
              <select
                value={filters.eventType}
                onChange={(e) => setFilters({...filters, eventType: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Event Types</option>
                <option value="processed">Processed</option>
                <option value="blocked">Blocked</option>
                <option value="redacted">Redacted</option>
                <option value="warned">Warned</option>
                <option value="error">Error</option>
              </select>
            </div>

            <div className="flex-1 min-w-48">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Risk Category</label>
              <select
                value={filters.riskCategories.length > 0 ? filters.riskCategories[0] : ''}
                onChange={(e) => setFilters({...filters, riskCategories: e.target.value ? [e.target.value] : []})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Categories</option>
                <option value="PROMPT_INJECTION">Prompt Injection</option>
                <option value="PII">PII</option>
                <option value="PHI">PHI</option>
                <option value="PCI">PCI</option>
              </select>
            </div>
            
            <div className="flex-1 min-w-48">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Severity</label>
              <select
                value={filters.severity}
                onChange={(e) => setFilters({...filters, severity: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={handleExportLogs}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors disabled:opacity-50"
                disabled={filteredLogs.length === 0}
              >
                Export CSV
              </button>
              <button
                onClick={() => setFilters({ eventType: '', severity: '', dateRange: '', riskCategories: [] })}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                Clear
              </button>
            </div>
          </div>
          
          <div className="mt-4 text-sm text-gray-600 dark:text-gray-300">
            Showing {paginatedLogs.length} of {filteredLogs.length} logs (Page {currentPage} of {totalPages || 1})
          </div>
        </div>

        {/* Log Table - Fixed Height and Scrollable */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 tracking-wider">
                    Event Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 tracking-wider">
                    Risk Categories
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 tracking-wider">
                    Severity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 tracking-wider">
                    Details Preview
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {paginatedLogs.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                      No logs found matching the current filters.
                    </td>
                  </tr>
                ) : (
                  paginatedLogs.map((log, index) => {
                    const riskCategories = getRiskCategoryBadges(log);
                    return (
                      <tr 
                        key={log.log_id || index} 
                        className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150 cursor-pointer"
                        onClick={() => handleRowClick(log)}
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getEventTypeBadge(log.event_type)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex flex-wrap gap-1">
                            {riskCategories.map((cat, i) => (
                              <span key={i} className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                                {cat}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getSeverityBadge(log.severity)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 max-w-xs">
                          <div className="truncate" title={JSON.stringify(log.details)}>
                            {log.details?.prompt ? log.details.prompt.substring(0, 100) + '...' : JSON.stringify(log.details).substring(0, 100) + '...'}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="bg-gray-50 dark:bg-gray-900 px-4 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    Showing <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> to <span className="font-medium">{Math.min(currentPage * itemsPerPage, filteredLogs.length)}</span> of <span className="font-medium">{filteredLogs.length}</span> results
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <button
                      onClick={() => setCurrentPage(1)}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                    >
                      First
                    </button>
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                    >
                      Previous
                    </button>
                    <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300">
                      Page {currentPage} of {totalPages}
                    </span>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-2 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                    >
                      Next
                    </button>
                    <button
                      onClick={() => setCurrentPage(totalPages)}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                    >
                      Last
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal for Log Details */}
      {isModalOpen && selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Log Details</h3>
              <button
                onClick={closeModal}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Timestamp</h4>
                <p className="text-gray-900 dark:text-gray-100">{new Date(selectedLog.timestamp).toLocaleString()}</p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Event Type</h4>
                <p>{getEventTypeBadge(selectedLog.event_type)}</p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Severity</h4>
                <p>{getSeverityBadge(selectedLog.severity)}</p>
              </div>

              <div>
                <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Risk Categories</h4>
                <div className="flex flex-wrap gap-2">
                  {getRiskCategoryBadges(selectedLog).map((cat, i) => (
                    <span key={i} className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                      {cat}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2 flex justify-between items-center">
                  <span>User Prompt</span>
                  {selectedLog.details?.prompt && (
                    <button
                      onClick={handleCopyPrompt}
                      className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Copy Prompt
                    </button>
                  )}
                </h4>
                <textarea
                  readOnly
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-gray-100 resize-none"
                  rows={8}
                  value={selectedLog.details?.prompt || selectedLog.metadata?.prompt || 'No prompt available'}
                />
              </div>

              {selectedLog.details?.reason && (
                <div>
                  <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Detection Reasons</h4>
                  <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg space-y-3">
                    {formatReasons(selectedLog.details.reason).map((reason, i) => (
                      <div key={i} className="border-l-3 border-red-500 pl-3">
                        {reason.category ? (
                          <>
                            <div className="flex items-start gap-2">
                              <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                              </svg>
                              <div className="flex-1">
                                <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                                  {reason.category}
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 font-mono">
                                  {reason.matches}
                                </p>
                              </div>
                            </div>
                          </>
                        ) : (
                          <div className="flex items-start gap-2">
                            <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <p className="text-sm text-gray-700 dark:text-gray-300">{reason.text || reason}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Technical Details</h4>
                <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded overflow-auto text-sm">
                  {JSON.stringify({
                    event_type: selectedLog.event_type,
                    severity: selectedLog.severity,
                    risk_categories: selectedLog.risk_categories,
                    risks_detected: selectedLog.details?.risks_detected,
                    rules_applied: selectedLog.details?.rules_applied
                  }, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}