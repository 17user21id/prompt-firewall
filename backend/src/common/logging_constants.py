"""
Logging-related constants for Prompt Firewall MVP.
"""

class LoggingConstants:
    """Logging-related constants."""
    
    # Default Configuration
    DEFAULT_LOGGER_NAME = "prompt_firewall"
    DEFAULT_LOG_DIR = "logs"
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    DEFAULT_BACKUP_COUNT = 5
    DEFAULT_DAYS_TO_KEEP = 30
    
    # Log Levels
    DEBUG_LEVEL = "DEBUG"
    INFO_LEVEL = "INFO"
    WARNING_LEVEL = "WARNING"
    ERROR_LEVEL = "ERROR"
    CRITICAL_LEVEL = "CRITICAL"
    
    # Log File Patterns
    LOG_FILE_PATTERN = "{}_{}_{}.log"
    DATE_FORMAT = "%Y-%m-%d"
    
    # Default Format String
    DEFAULT_FORMAT_STRING = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
    )
    
    # Environment Variables
    LOG_LEVEL_ENV = "LOG_LEVEL"
    LOG_DIR_ENV = "LOG_DIR"
    LOG_MAX_FILE_SIZE_ENV = "LOG_MAX_FILE_SIZE"
    LOG_BACKUP_COUNT_ENV = "LOG_BACKUP_COUNT"
    LOG_FORMAT_ENV = "LOG_FORMAT"
    
    # Log Messages
    STARTING_OPERATION = "Starting {}"
    COMPLETED_OPERATION = "Completed {} in {:.3f}s"
    FAILED_OPERATION = "Failed {} after {:.3f}s: {}"
    CLEANED_OLD_LOGS = "Cleaned up {} old log files"
    
    # Context Keys
    CONTEXT_PREFIX = "Context: "
    OPERATION_KEY = "operation"
    DURATION_KEY = "duration"
    ERROR_KEY = "error"
