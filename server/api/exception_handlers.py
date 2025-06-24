from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler

ERROR_CODES_MAP = {"no_active_account": "authentication_failed"}


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    error_code = "error"
    message = "An error occurred."
    details = None
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, DRFValidationError):
        error_code = "validation_error"
        message = "Validation failed."
        details = response.data if response else None
        status_code = status.HTTP_400_BAD_REQUEST
    elif response is not None:
        error_code = getattr(exc, "code", error_code)
        status_code = response.status_code
        detail = response.data.get("detail", None)

        if isinstance(detail, list):
            message = ", ".join(str(d) for d in detail)
        else:
            message = str(detail)

        if code := getattr(detail, "code", None):
            error_code = code

    error_message = {
        "error": {
            "code": ERROR_CODES_MAP.get(error_code, error_code),
            "message": message,
        }
    }

    if details:
        error_message["error"]["details"] = details

    if response is not None:
        response.data = error_message
        response.status_code = status_code

    return response
