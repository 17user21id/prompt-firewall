# Prompt Firewall SDK

import requests
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

class PromptFirewallSDK:
    """Python SDK for Prompt Firewall API."""
    
    def __init__(self, api_url: str, api_key: str, tenant_id: str):
        """
        Initialize the SDK.
        
        Args:
            api_url: Base URL of the Prompt Firewall API
            api_key: API key for authentication
            tenant_id: Tenant ID for the requests
        """
        self.api_url = api_url.rstrip('/')
        self.tenant_id = tenant_id
        self.headers = {
            "Authorization": f"Bearer {tenant_id}:{api_key}",
            "Content-Type": "application/json"
        }
    
    def create_tenant(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new tenant.
        
        Args:
            name: Name of the tenant
            metadata: Optional metadata for the tenant
            
        Returns:
            Dict containing tenant information including tenant_id and api_key
        """
        data = {"name": name}
        if metadata:
            data["metadata"] = metadata
        
        response = requests.post(
            f"{self.api_url}/v1/tenants",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def query(self, prompt: str, user_id: Optional[str] = None, 
              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a prompt through the firewall.
        
        Args:
            prompt: The prompt text to analyze
            user_id: Optional user ID
            metadata: Optional metadata
            
        Returns:
            Dict containing analysis results
        """
        data = {
            "tenant_id": self.tenant_id,
            "prompt": prompt
        }
        if user_id:
            data["user_id"] = user_id
        if metadata:
            data["metadata"] = metadata
        
        response = requests.post(
            f"{self.api_url}/v1/query",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_logs(self, event_type: Optional[str] = None, 
                 date_from: Optional[str] = None, date_to: Optional[str] = None,
                 user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve logs for the tenant.
        
        Args:
            event_type: Filter by event type
            date_from: Filter from date (ISO format)
            date_to: Filter to date (ISO format)
            user_id: Filter by user ID
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        params = {"tenant_id": self.tenant_id}
        if event_type:
            params["event_type"] = event_type
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if user_id:
            params["user_id"] = user_id
        if limit:
            params["limit"] = limit
        
        response = requests.get(
            f"{self.api_url}/v1/logs",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_prompts(self, decision: Optional[str] = None,
                   date_from: Optional[str] = None, date_to: Optional[str] = None,
                   user_id: Optional[str] = None, has_risks: Optional[bool] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve prompt history for the tenant.
        
        Args:
            decision: Filter by decision (block, redact, warn, allow)
            date_from: Filter from date (ISO format)
            date_to: Filter to date (ISO format)
            user_id: Filter by user ID
            has_risks: Filter by presence of risks
            limit: Maximum number of prompts to return
            
        Returns:
            List of prompt entries
        """
        params = {"tenant_id": self.tenant_id}
        if decision:
            params["decision"] = decision
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if user_id:
            params["user_id"] = user_id
        if has_risks is not None:
            params["has_risks"] = has_risks
        if limit:
            params["limit"] = limit
        
        response = requests.get(
            f"{self.api_url}/v1/prompts",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_rule(self, rule_type: str, pattern: str, action: str, 
                   severity: str, description: Optional[str] = None,
                   enabled: bool = True) -> Dict[str, Any]:
        """
        Create a new rule for the tenant.
        
        Args:
            rule_type: Type of rule (PII, injection, etc.)
            pattern: Regex pattern for detection
            action: Action to take (block, redact, warn, allow)
            severity: Severity level (low, medium, high)
            description: Optional description
            enabled: Whether the rule is enabled
            
        Returns:
            Dict containing rule information
        """
        data = {
            "type": rule_type,
            "pattern": pattern,
            "action": action,
            "severity": severity,
            "enabled": enabled
        }
        if description:
            data["description"] = description
        
        response = requests.post(
            f"{self.api_url}/v1/rules",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_rules(self, rule_type: Optional[str] = None,
                 action: Optional[str] = None, severity: Optional[str] = None,
                 enabled: Optional[bool] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve rules for the tenant.
        
        Args:
            rule_type: Filter by rule type
            action: Filter by action
            severity: Filter by severity
            enabled: Filter by enabled status
            limit: Maximum number of rules to return
            
        Returns:
            List of rule entries
        """
        params = {"tenant_id": self.tenant_id}
        if rule_type:
            params["type"] = rule_type
        if action:
            params["action"] = action
        if severity:
            params["severity"] = severity
        if enabled is not None:
            params["enabled"] = enabled
        if limit:
            params["limit"] = limit
        
        response = requests.get(
            f"{self.api_url}/v1/rules",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_rule(self, rule_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing rule.
        
        Args:
            rule_id: ID of the rule to update
            **kwargs: Fields to update (type, pattern, action, severity, etc.)
            
        Returns:
            Dict containing updated rule information
        """
        response = requests.put(
            f"{self.api_url}/v1/rules/{rule_id}",
            json=kwargs,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def delete_rule(self, rule_id: str) -> Dict[str, str]:
        """
        Delete a rule.
        
        Args:
            rule_id: ID of the rule to delete
            
        Returns:
            Dict with success message
        """
        response = requests.delete(
            f"{self.api_url}/v1/rules/{rule_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for the tenant.
        
        Returns:
            Dict containing tenant, prompt, rule, and log statistics
        """
        response = requests.get(
            f"{self.api_url}/v1/stats",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health.
        
        Returns:
            Dict containing health status
        """
        response = requests.get(f"{self.api_url}/health")
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    # Initialize SDK
    sdk = PromptFirewallSDK(
        api_url="http://localhost:8000",
        api_key="your-api-key",
        tenant_id="your-tenant-id"
    )
    
    # Check health
    health = sdk.health_check()
    print(f"API Status: {health['status']}")
    
    # Process a prompt
    result = sdk.query("My email is john@example.com")
    print(f"Decision: {result['decision']}")
    print(f"Risks detected: {len(result['risks'])}")
    
    # Get recent logs
    logs = sdk.get_logs(limit=10)
    print(f"Recent logs: {len(logs)}")
    
    # Get statistics
    stats = sdk.get_stats()
    print(f"Total prompts processed: {stats.get('prompt_stats', {}).get('total_prompts', 0)}")
