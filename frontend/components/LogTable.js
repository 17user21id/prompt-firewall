import { useState, useMemo } from 'react';
import { saveAs } from 'file-saver';

export default function LogTable({ logs = [], loading = false }) {
  const [filters, setFilters] = useState({
    eventType: '',
    severity: '',
    dateRange: ''
  });

  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      if (filters.eventType && log.event_type !== filters.eventType) return false;
      if (filters.severity && log.severity !== filters.severity) return false;
      if (filters.dateRange) {
        const logDate = new Date(log.timestamp);
        const filterDate = new Date(filters.dateRange);
        if (logDate < filterDate) return false;
      }
      return true;
    });
  }, [logs, filters]);

  const exportLogs = () => {
    if (filteredLogs.length === 0) {
      toast.error('No logs to export');
      return;
    }

    const csvContent = [
      ['Log ID', 'Prompt ID', 'Event Type', 'Severity', 'Details', 'Timestamp'],
      ...filteredLogs.map(log => [
        log.log_id,
        log.prompt_id || 'N/A',
        log.event_type,
        log.severity || 'N/A',
        JSON.stringify(log.details),
        new Date(log.timestamp).toISOString()
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getSeverityBadge = (severity) => {
    const severityClasses = {
      critical: 'badge-error',
      high: 'badge-warning',
      medium: 'badge-info',
      low: 'badge-success'
    };
    
    return (
      <span className={`badge ${severityClasses[severity] || 'badge-info'}`}>
        {severity || 'N/A'}
      </span>
    );
  };

  const getEventTypeBadge = (eventType) => {
    const eventClasses = {
      processed: 'badge-success',
      blocked: 'badge-error',
      redacted: 'badge-warning',
      warned: 'badge-info',
      error: 'badge-error'
    };
    
    return (
      <span className={`badge ${eventClasses[eventType] || 'badge-info'}`}>
        {eventType}
      </span>
    );
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
    <div className="space-y-6">
      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-48">
            <label className="form-label">Event Type</label>
            <select
              value={filters.eventType}
              onChange={(e) => setFilters({...filters, eventType: e.target.value})}
              className="input-field"
              aria-label="Filter Logs by Event Type"
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
            <label className="form-label">Severity</label>
            <select
              value={filters.severity}
              onChange={(e) => setFilters({...filters, severity: e.target.value})}
              className="input-field"
              aria-label="Filter Logs by Severity"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          
          <div className="flex-1 min-w-48">
            <label className="form-label">From Date</label>
            <input
              type="date"
              value={filters.dateRange}
              onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
              className="input-field"
              aria-label="Filter Logs by Date"
            />
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={exportLogs}
              className="btn-secondary"
              aria-label="Export Logs as CSV"
              disabled={filteredLogs.length === 0}
            >
              Export CSV
            </button>
            <button
              onClick={() => setFilters({ eventType: '', severity: '', dateRange: '' })}
              className="btn-secondary"
              aria-label="Clear Filters"
            >
              Clear Filters
            </button>
          </div>
        </div>
        
        <div className="mt-4 text-sm text-gray-600 dark:text-gray-300">
          Showing {filteredLogs.length} of {logs.length} logs
        </div>
      </div>

      {/* Log Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200" aria-label="Logs Table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Log ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Event Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    No logs found matching the current filters.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.log_id} className="hover:bg-gray-50 transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                      {log.log_id.slice(0, 8)}...
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getEventTypeBadge(log.event_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getSeverityBadge(log.severity)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs">
                      <div className="truncate" title={JSON.stringify(log.details)}>
                        {JSON.stringify(log.details)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
