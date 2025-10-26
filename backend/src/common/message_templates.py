"""
Message templates for consistent formatting in Prompt Firewall MVP.
"""

class MessageTemplates:
    """Message templates for consistent formatting."""
    
    # Error Templates
    ERROR_TEMPLATE = "{}: {}"
    VALIDATION_ERROR_TEMPLATE = "{} validation failed: {}"
    
    # Success Templates
    SUCCESS_TEMPLATE = "{} completed successfully"
    CREATED_TEMPLATE = "{} created successfully"
    UPDATED_TEMPLATE = "{} updated successfully"
    DELETED_TEMPLATE = "{} deleted successfully"
    
    # Log Templates
    LOG_TEMPLATE = "{}: {}"
    OPERATION_TEMPLATE = "{} operation: {}"
    EVENT_TEMPLATE = "{} event: {}"
    
    # Context Templates
    CONTEXT_TEMPLATE = "{} | Context: {}"
    DURATION_TEMPLATE = "{} completed in {:.3f}s"
    ERROR_WITH_CONTEXT_TEMPLATE = "{} failed: {} | Context: {}"
