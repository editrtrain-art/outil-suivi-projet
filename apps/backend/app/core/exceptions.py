"""Domain-level exception hierarchy.

These exceptions are infrastructure-agnostic so the domain layer can
signal errors without importing HTTP or database-specific modules.
Exception handlers in the API layer translate them to proper HTTP responses.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base exception for all domain-level errors.

    Attributes:
        message: Human-readable error description.
    """

    def __init__(self, message: str = "A domain error occurred") -> None:
        self.message: str = message
        super().__init__(self.message)


class NotFoundError(DomainError):
    """Raised when a requested resource does not exist (maps to HTTP 404).

    Attributes:
        resource: The type of resource that was not found.
        resource_id: Identifier of the missing resource.
    """

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: str | int = "",
    ) -> None:
        self.resource: str = resource
        self.resource_id: str | int = resource_id
        super().__init__(f"{resource} not found: {resource_id}")


class ForbiddenError(DomainError):
    """Raised when the caller lacks permission (maps to HTTP 403).

    Attributes:
        action: The action that was denied.
    """

    def __init__(self, action: str = "this action") -> None:
        self.action: str = action
        super().__init__(f"Forbidden: insufficient permissions for {action}")


class ConflictError(DomainError):
    """Raised on uniqueness or state conflicts (maps to HTTP 409).

    Attributes:
        detail: Explanation of the conflict.
    """

    def __init__(self, detail: str = "Resource conflict") -> None:
        self.detail: str = detail
        super().__init__(detail)


class ValidationError(DomainError):
    """Raised when domain-level validation fails (maps to HTTP 422).

    Attributes:
        errors: Mapping of field names to error messages.
    """

    def __init__(
        self,
        errors: dict[str, str] | None = None,
        message: str = "Validation failed",
    ) -> None:
        self.errors: dict[str, str] = errors or {}
        super().__init__(message)


class CircularDependencyError(DomainError):
    """Raised when a circular dependency is detected in the CPM graph.

    Attributes:
        cycle: Ordered list of node identifiers forming the cycle.
    """

    def __init__(self, cycle: list[str] | None = None) -> None:
        self.cycle: list[str] = cycle or []
        detail = f"Circular dependency detected: {' -> '.join(self.cycle)}" if self.cycle else "Circular dependency detected"
        super().__init__(detail)
