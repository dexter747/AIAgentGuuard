"""
AgentGuard exceptions
"""


class AgentGuardError(Exception):
    """Base exception for AgentGuard SDK."""
    pass


class AuthenticationError(AgentGuardError):
    """Raised when API key is invalid."""
    pass


class RateLimitError(AgentGuardError):
    """Raised when rate limit is exceeded."""
    pass


class ValidationError(AgentGuardError):
    """Raised when request data is invalid."""
    pass


class NetworkError(AgentGuardError):
    """Raised when network request fails."""
    pass
