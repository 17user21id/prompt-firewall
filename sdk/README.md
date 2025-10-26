# Prompt Firewall SDK

A Python SDK for the Prompt Firewall API that provides easy integration for detecting PII and prompt injection attempts.

## Installation

```bash
pip install prompt-firewall-sdk
```

## Quick Start

```python
from prompt_firewall import PromptFirewallSDK

# Initialize the SDK
sdk = PromptFirewallSDK(
    api_url="https://your-api-domain.com",
    api_key="your-api-key",
    tenant_id="your-tenant-id"
)

# Process a prompt
result = sdk.query("My email is john@example.com")
print(f"Decision: {result['decision']}")
print(f"Risks detected: {len(result['risks'])}")

# Get statistics
stats = sdk.get_stats()
print(f"Total prompts: {stats['prompt_stats']['total_prompts']}")
```

## API Reference

### PromptFirewallSDK

#### Constructor

```python
PromptFirewallSDK(api_url: str, api_key: str, tenant_id: str)
```

#### Methods

- `query(prompt: str, user_id: str = None, metadata: dict = None)` - Process a prompt
- `get_logs(event_type: str = None, date_from: str = None, date_to: str = None, user_id: str = None, limit: int = 100)` - Get logs
- `get_prompts(decision: str = None, date_from: str = None, date_to: str = None, user_id: str = None, has_risks: bool = None, limit: int = 100)` - Get prompt history
- `create_rule(rule_type: str, pattern: str, action: str, severity: str, description: str = None, enabled: bool = True)` - Create a rule
- `get_rules(rule_type: str = None, action: str = None, severity: str = None, enabled: bool = None, limit: int = 100)` - Get rules
- `update_rule(rule_id: str, **kwargs)` - Update a rule
- `delete_rule(rule_id: str)` - Delete a rule
- `get_stats()` - Get comprehensive statistics
- `health_check()` - Check API health

## Examples

### Basic Usage

```python
# Initialize SDK
sdk = PromptFirewallSDK(
    api_url="http://localhost:8000",
    api_key="your-api-key",
    tenant_id="your-tenant-id"
)

# Process a prompt
result = sdk.query("Contact me at john@example.com")
print(f"Decision: {result['decision']}")
print(f"Modified prompt: {result['promptModified']}")
```

### Rule Management

```python
# Create a custom rule
rule = sdk.create_rule(
    rule_type="CUSTOM",
    pattern=r"\b(confidential|secret)\b",
    action="warn",
    severity="medium",
    description="Detect confidential information"
)

# Get all rules
rules = sdk.get_rules()
for rule in rules:
    print(f"Rule: {rule['type']} - {rule['action']}")

# Update a rule
sdk.update_rule(rule['rule_id'], enabled=False)
```

### Logging and Monitoring

```python
# Get recent logs
logs = sdk.get_logs(limit=50)
for log in logs:
    print(f"{log['timestamp']}: {log['event_type']} - {log['details']}")

# Get statistics
stats = sdk.get_stats()
print(f"Total prompts: {stats['prompt_stats']['total_prompts']}")
print(f"Blocked prompts: {stats['prompt_stats']['blocked_prompts']}")
print(f"PII detections: {stats['prompt_stats']['pii_detections']}")
```

## Error Handling

The SDK raises `requests.HTTPError` for HTTP errors. Handle them appropriately:

```python
import requests

try:
    result = sdk.query("test prompt")
except requests.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed")
    elif e.response.status_code == 429:
        print("Rate limit exceeded")
    else:
        print(f"API error: {e}")
```

## License

MIT License - see LICENSE file for details.
