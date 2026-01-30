"""
MH1 MCP Client
Handles connections to MCP servers (HubSpot, Snowflake, etc.)
with retry logic and error handling.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Callable, Dict, Tuple
from functools import wraps

SYSTEM_ROOT = Path(__file__).parent.parent


@dataclass
class MCPResponse:
    """Standardized response from MCP calls."""
    success: bool
    data: Any
    error: Optional[str] = None
    duration_ms: int = 0
    retries: int = 0


class CircuitBreaker:
    """
    Circuit breaker pattern for external API calls.
    Opens after consecutive failures, resets after cooldown.
    """
    
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "open"

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if time.time() - self.last_failure_time > self.cooldown_seconds:
                self.state = "half-open"
                return True
            return False
        return True  # half-open allows one try


def with_retry(max_retries: int = 3, backoff_base: float = 1.0):
    """
    Decorator for retry with exponential backoff.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        wait = backoff_base * (2 ** attempt)
                        time.sleep(wait)
            raise last_error
        return wrapper
    return decorator


class MCPClient:
    """
    Client for MCP server interactions.
    
    Note: In Cursor/Claude Code, MCP calls are made through the built-in tools.
    This client provides a wrapper with:
    - Retry logic
    - Circuit breaker
    - Telemetry logging
    - Standardized error handling
    """
    
    def __init__(self, server_name: str, cache_ttl_seconds: int = 3600):
        self.server_name = server_name
        self.circuit_breaker = CircuitBreaker()
        self._idempotency_cache: Dict[str, Tuple[MCPResponse, float]] = {}
        self._cache_ttl_seconds = cache_ttl_seconds  # 1 hour default
        self._load_config()

    def _load_config(self):
        """Load MCP server config."""
        config_path = SYSTEM_ROOT / "config" / "mcp-servers.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                self.config = config.get("servers", {}).get(self.server_name, {})
        else:
            self.config = {}

    def is_available(self) -> bool:
        """Check if MCP server is available."""
        return self.circuit_breaker.can_execute()

    def call(
        self,
        tool_name: str,
        params: dict,
        timeout_seconds: int = 30,
        idempotency_key: str = None
    ) -> MCPResponse:
        """
        Make an MCP tool call.
        
        In practice, the actual MCP call is made by Claude Code's tool system.
        This wrapper handles the response standardization.
        
        Args:
            tool_name: The MCP tool to call (e.g., 'hubspot_search_contacts')
            params: Parameters for the tool
            timeout_seconds: Request timeout
            idempotency_key: Optional key for idempotent requests. If provided and
                           cached, returns cached result instead of making new call.
            
        Returns:
            MCPResponse with standardized format
        """
        # Check cache if idempotency key provided
        if idempotency_key and idempotency_key in self._idempotency_cache:
            cached_response, cached_time = self._idempotency_cache[idempotency_key]
            # Check if cache entry is still valid (not expired)
            if time.time() - cached_time < self._cache_ttl_seconds:
                return cached_response
            else:
                # Expired entry, remove it
                del self._idempotency_cache[idempotency_key]
        
        if not self.circuit_breaker.can_execute():
            return MCPResponse(
                success=False,
                data=None,
                error=f"Circuit breaker open for {self.server_name}. Retry after cooldown."
            )
        
        start_time = time.time()
        
        # This is where the actual MCP call would happen
        # In Claude Code, this is handled by the tool system
        # Here we just return a placeholder for the interface
        
        # Simulate the call structure
        call_spec = {
            "server": self.server_name,
            "tool": tool_name,
            "params": params,
            "timeout": timeout_seconds
        }
        
        duration = int((time.time() - start_time) * 1000)
        
        response = MCPResponse(
            success=True,
            data=call_spec,  # Would be actual response data
            duration_ms=duration
        )
        
        # Cache result if idempotency key provided and call was successful
        if idempotency_key and response.success:
            self._idempotency_cache[idempotency_key] = (response, time.time())
        
        return response

    def clear_idempotency_cache(self):
        """Clear all cached idempotency responses."""
        self._idempotency_cache.clear()

    def call_with_retry(
        self,
        tool_name: str,
        params: dict,
        max_retries: int = 3,
        idempotency_key: str = None
    ) -> MCPResponse:
        """Make MCP call with retry logic."""
        last_error = None
        
        for attempt in range(max_retries + 1):
            response = self.call(tool_name, params, idempotency_key=idempotency_key)
            
            if response.success:
                self.circuit_breaker.record_success()
                response.retries = attempt
                return response
            
            last_error = response.error
            self.circuit_breaker.record_failure()
            
            if attempt < max_retries:
                wait = 2 ** attempt
                time.sleep(wait)
        
        return MCPResponse(
            success=False,
            data=None,
            error=last_error,
            retries=max_retries
        )


# Convenience classes for specific MCP servers

class HubSpotClient(MCPClient):
    """HubSpot MCP client with typed methods."""
    
    def __init__(self):
        super().__init__("hubspot")

    def search_contacts(self, email: str = None, limit: int = 10, properties: str = None) -> MCPResponse:
        params = {"limit": limit}
        if email:
            params["email"] = email
        if properties:
            params["properties"] = properties
        return self.call_with_retry("hubspot_search_contacts", params)

    def get_contact(self, contact_id: str = None, email: str = None, properties: str = None) -> MCPResponse:
        params = {}
        if contact_id:
            params["contact_id"] = contact_id
        if email:
            params["email"] = email
        if properties:
            params["properties"] = properties
        return self.call_with_retry("hubspot_get_contact", params)

    def list_contacts(self, lifecyclestage: str = None, limit: int = 10, properties: str = None) -> MCPResponse:
        params = {"limit": limit}
        if lifecyclestage:
            params["lifecyclestage"] = lifecyclestage
        if properties:
            params["properties"] = properties
        return self.call_with_retry("hubspot_list_contacts", params)

    def list_companies(self, limit: int = 10, properties: str = None) -> MCPResponse:
        params = {"limit": limit}
        if properties:
            params["properties"] = properties
        return self.call_with_retry("hubspot_list_companies", params)

    def get_company(self, company_id: str, properties: str = None) -> MCPResponse:
        params = {"company_id": company_id}
        if properties:
            params["properties"] = properties
        return self.call_with_retry("hubspot_get_company", params)


class SnowflakeClient(MCPClient):
    """Snowflake MCP client with typed methods."""
    
    def __init__(self):
        super().__init__("snowflake")

    def execute_query(self, query: str, limit: int = 100) -> MCPResponse:
        return self.call_with_retry("snowflake_execute_query", {
            "query": query,
            "limit": limit
        })

    def list_databases(self) -> MCPResponse:
        return self.call_with_retry("snowflake_list_databases", {})

    def list_tables(self, database: str = None, schema: str = None) -> MCPResponse:
        params = {}
        if database:
            params["database"] = database
        if schema:
            params["schema"] = schema
        return self.call_with_retry("snowflake_list_tables", params)

    def describe_table(self, table_name: str, database: str = None, schema: str = None) -> MCPResponse:
        params = {"table_name": table_name}
        if database:
            params["database"] = database
        if schema:
            params["schema"] = schema
        return self.call_with_retry("snowflake_describe_table", params)


# Factory function
def get_client(server_name: str) -> MCPClient:
    """Get MCP client by server name."""
    clients = {
        "hubspot": HubSpotClient,
        "snowflake": SnowflakeClient,
    }
    client_class = clients.get(server_name, MCPClient)
    return client_class() if server_name in clients else MCPClient(server_name)


if __name__ == "__main__":
    # Test clients
    hs = HubSpotClient()
    print(f"HubSpot available: {hs.is_available()}")
    
    sf = SnowflakeClient()
    print(f"Snowflake available: {sf.is_available()}")
