"""
Custom DRF exception handler that guarantees every error response
follows the standard Brightside envelope:
{"success": false, "message": "...", "errors": {...}}
"""
import logging

from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("brightside")


class ServiceError(Exception):
    """Raised by the service layer for expected/business-logic errors."""

    def __init__(self, message: str, errors=None, status_code: int = 400):
        self.message = message
        self.errors = errors or {}
        self.status_code = status_code
        super().__init__(message)


class NotFoundServiceError(ServiceError):
    def __init__(self, message="Resource not found", errors=None):
        super().__init__(message, errors, status_code=404)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if isinstance(exc, ServiceError):
        logger.warning("ServiceError: %s | errors=%s", exc.message, exc.errors)
        from rest_framework.response import Response

        return Response(
            {"success": False, "message": exc.message, "errors": exc.errors},
            status=exc.status_code,
        )

    if response is not None:
        errors = response.data
        message = "Request failed"
        if isinstance(errors, dict) and "detail" in errors:
            message = str(errors["detail"])
        response.data = {
            "success": False,
            "message": message,
            "errors": errors if isinstance(errors, dict) else {"detail": errors},
        }
        logger.warning("API error [%s]: %s", response.status_code, response.data)
        return response

    logger.exception("Unhandled exception: %s", exc)
    return None
