from __future__ import annotations


class DomainError(Exception):
    """Base exception for domain errors."""


class ConversationNotFoundError(DomainError):
    """Raised when a conversation cannot be found."""


class InvalidAgentConfigError(DomainError):
    """Raised when an agent configuration is invalid."""


class ContractValidationError(DomainError):
    """Raised when a UI component payload fails contract validation."""
