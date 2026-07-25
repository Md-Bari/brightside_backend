"""
Structured request/response logging middleware.
Logs method, path, status code and latency. Never logs API keys or
Authorization headers.
"""
import logging
import time

logger = logging.getLogger("brightside")

SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}


class RequestResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        logger.info("REQUEST %s %s", request.method, request.get_full_path())

        response = self.get_response(request)

        duration_ms = round((time.monotonic() - start) * 1000, 2)
        logger.info(
            "RESPONSE %s %s -> %s (%.2fms)",
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
        )
        return response
