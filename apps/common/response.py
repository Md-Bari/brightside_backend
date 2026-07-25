"""
Standard API response envelope used across all Brightside endpoints.
"""
from rest_framework.response import Response


def success_response(data=None, message="Success", status_code=200, meta=None):
    payload = {
        "success": True,
        "message": message,
        "data": data if data is not None else {},
    }
    if meta:
        payload["meta"] = meta
    return Response(payload, status=status_code)


def error_response(message="Something went wrong", errors=None, status_code=400):
    payload = {
        "success": False,
        "message": message,
        "errors": errors if errors is not None else {},
    }
    return Response(payload, status=status_code)
