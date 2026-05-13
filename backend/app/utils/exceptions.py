"""Custom exceptions."""


class SaarTURNierException(Exception):
    """Base exception for saarTURNier."""

    pass


class ValidationError(SaarTURNierException):
    """Validation error."""

    pass


class NotFoundError(SaarTURNierException):
    """Resource not found error."""

    pass


class AuthenticationError(SaarTURNierException):
    """Authentication error."""

    pass


class AuthorizationError(SaarTURNierException):
    """Authorization error."""

    pass


class StateTransitionError(SaarTURNierException):
    """Invalid state transition error."""

    pass


class FairnessViolationError(SaarTURNierException):
    """Fairness invariant violation error."""

    pass
