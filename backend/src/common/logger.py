"""
Smart Logger Implementation with Multiple Levels and Date-wise File Creation.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
from logging.handlers import RotatingFileHandler
from .logging_constants import LoggingConstants
from .message_templates import MessageTemplates
from .auth_constants import AuthConstants
from .firewall_constants import FirewallConstants

class SmartLogger:
    """
    Smart logger that creates separate log files for different levels
    and organizes them by date.
    """
    
    def __init__(self, 
                 name: str = LoggingConstants.DEFAULT_LOGGER_NAME,
                 log_dir: str = LoggingConstants.DEFAULT_LOG_DIR,
                 level: str = LoggingConstants.DEFAULT_LOG_LEVEL,
                 max_file_size: int = LoggingConstants.DEFAULT_MAX_FILE_SIZE,  # 10MB
                 backup_count: int = LoggingConstants.DEFAULT_BACKUP_COUNT,
                 format_string: Optional[str] = None):
        """
        Initialize the smart logger.
        
        Args:
            name: Logger name
            log_dir: Directory to store log files
            level: Default log level
            max_file_size: Maximum size of each log file in bytes
            backup_count: Number of backup files to keep
            format_string: Custom format string for logs
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Default format string
        if format_string is None:
            self.format_string = LoggingConstants.DEFAULT_FORMAT_STRING
        else:
            self.format_string = format_string
        
        # Create formatter
        self.formatter = logging.Formatter(self.format_string)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Add console handler
        self._add_console_handler()
        
        # Add file handlers for different levels
        self._add_file_handlers()
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _add_console_handler(self):
        """Add console handler for immediate output."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handlers(self):
        """Add file handlers for different log levels."""
        today = datetime.now().strftime(LoggingConstants.DATE_FORMAT)
        
        # Define log levels and their corresponding files
        log_levels = {
            LoggingConstants.DEBUG_LEVEL: LoggingConstants.LOG_FILE_PATTERN.format(self.name, "debug", today),
            LoggingConstants.INFO_LEVEL: LoggingConstants.LOG_FILE_PATTERN.format(self.name, "info", today),
            LoggingConstants.WARNING_LEVEL: LoggingConstants.LOG_FILE_PATTERN.format(self.name, "warning", today),
            LoggingConstants.ERROR_LEVEL: LoggingConstants.LOG_FILE_PATTERN.format(self.name, "error", today),
            LoggingConstants.CRITICAL_LEVEL: LoggingConstants.LOG_FILE_PATTERN.format(self.name, "critical", today)
        }
        
        for level_name, filename in log_levels.items():
            level = getattr(logging, level_name)
            
            # Create file handler with rotation
            file_path = self.log_dir / filename
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            
            # Set level for this handler
            file_handler.setLevel(level)
            
            # Set formatter
            file_handler.setFormatter(self.formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log message with additional context."""
        # Standard logging kwargs that Python's logging module accepts
        standard_kwargs = ['exc_info', 'stack_info', 'stacklevel', 'extra']
        extra_context = {}
        
        # Separate standard logging kwargs from custom context
        log_kwargs = {}
        for key, value in kwargs.items():
            if key in standard_kwargs:
                log_kwargs[key] = value
            else:
                extra_context[key] = value
        
        # Add context to the message if provided
        if extra_context:
            context_str = json.dumps(extra_context, default=str)
            message = f"{message} | Context: {context_str}"
        
        self.logger.log(level, message, **log_kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self._log_with_context(logging.ERROR, message, exc_info=True, **kwargs)
    
    def log_auth_event(self, event_type: str, tenant_id: str, details: Dict[str, Any]):
        """Log authentication events."""
        self.info(
            MessageTemplates.EVENT_TEMPLATE.format("Authentication", event_type),
            event_type=event_type,
            tenant_id=tenant_id,
            details=details
        )
    
    def log_api_request(self, method: str, endpoint: str, tenant_id: str, 
                       status_code: int, response_time: float, **kwargs):
        """Log API requests."""
        self.info(
            MessageTemplates.OPERATION_TEMPLATE.format(AuthConstants.API_REQUEST_PREFIX.format(method, endpoint)),
            method=method,
            endpoint=endpoint,
            tenant_id=tenant_id,
            status_code=status_code,
            response_time_ms=round(response_time * 1000, 2),
            **kwargs
        )
    
    def log_security_event(self, event_type: str, severity: str, details: Dict[str, Any]):
        """Log security events."""
        level_map = {
            FirewallConstants.SEVERITY_LOW: logging.INFO,
            FirewallConstants.SEVERITY_MEDIUM: logging.WARNING,
            FirewallConstants.SEVERITY_HIGH: logging.ERROR,
            FirewallConstants.SEVERITY_CRITICAL: logging.CRITICAL
        }
        
        level = level_map.get(severity.lower(), logging.WARNING)
        
        self._log_with_context(
            level,
            MessageTemplates.EVENT_TEMPLATE.format(AuthConstants.SECURITY_EVENT_PREFIX.format(event_type)),
            event_type=event_type,
            severity=severity,
            details=details
        )
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        self.info(
            MessageTemplates.DURATION_TEMPLATE.format(
                MessageTemplates.OPERATION_TEMPLATE.format(AuthConstants.PERFORMANCE_PREFIX.format(operation)),
                duration
            ),
            operation=operation,
            duration=duration,
            **kwargs
        )
    
    def log_database_operation(self, operation: str, collection: str, 
                              tenant_id: str, success: bool, **kwargs):
        """Log database operations."""
        level = logging.INFO if success else logging.ERROR
        
        self._log_with_context(
            level,
            MessageTemplates.OPERATION_TEMPLATE.format(AuthConstants.DATABASE_OPERATION_PREFIX.format(operation, collection)),
            operation=operation,
            collection=collection,
            tenant_id=tenant_id,
            success=success,
            **kwargs
        )
    
    def get_log_files(self) -> Dict[str, str]:
        """Get list of current log files."""
        log_files = {}
        today = datetime.now().strftime("%Y-%m-%d")
        
        for level in [LoggingConstants.DEBUG_LEVEL, LoggingConstants.INFO_LEVEL, LoggingConstants.WARNING_LEVEL, LoggingConstants.ERROR_LEVEL, LoggingConstants.CRITICAL_LEVEL]:
            filename = LoggingConstants.LOG_FILE_PATTERN.format(self.name, level.lower(), today)
            file_path = self.log_dir / filename
            log_files[level] = str(file_path) if file_path.exists() else None
        
        return log_files
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files."""
        import glob
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Find all log files
        pattern = str(self.log_dir / f"{self.name}_*.log")
        log_files = glob.glob(pattern)
        
        cleaned_count = 0
        for log_file in log_files:
            try:
                # Extract date from filename
                filename = Path(log_file).name
                parts = filename.split('_')
                if len(parts) >= 3:
                    date_str = parts[-1].replace('.log', '')
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    if file_date < cutoff_date:
                        os.remove(log_file)
                        cleaned_count += 1
            except (ValueError, IndexError):
                # Skip files that don't match expected format
                continue
        
        self.info(LoggingConstants.CLEANED_OLD_LOGS.format(cleaned_count))
        return cleaned_count

# Global logger instance
logger = SmartLogger()

# Convenience functions for easy access
def get_logger(name: str = None) -> SmartLogger:
    """Get logger instance."""
    if name:
        return SmartLogger(name=name)
    return logger

def debug(message: str, **kwargs):
    """Log debug message."""
    logger.debug(message, **kwargs)

def info(message: str, **kwargs):
    """Log info message."""
    logger.info(message, **kwargs)

def warning(message: str, **kwargs):
    """Log warning message."""
    logger.warning(message, **kwargs)

def error(message: str, **kwargs):
    """Log error message."""
    logger.error(message, **kwargs)

def critical(message: str, **kwargs):
    """Log critical message."""
    logger.critical(message, **kwargs)

def exception(message: str, **kwargs):
    """Log exception with traceback."""
    logger.exception(message, **kwargs)

# Context manager for logging
class LogContext:
    """Context manager for structured logging."""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.info(LoggingConstants.STARTING_OPERATION.format(self.operation), **self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            message = LoggingConstants.COMPLETED_OPERATION.format(self.operation, duration)
            logger.info(message, **self.context)
        else:
            message = LoggingConstants.FAILED_OPERATION.format(self.operation, duration, str(exc_val))
            logger.error(message, **self.context)
