# utils/exception_handler.py
import logging
from django.shortcuts import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "success": False,
            "code": response.status_code,
            "message": response.data.get("detail", response.reason_phrase),
            "data": None,
            "details": None,  # اینجا می‌توانید فیلد به فیلد خطا را اضافه کنید
            "meta": {
                "request_id": None,  # در اینجا نیاز به لاگ گرفتن دستی دارید یا از Middleware استفاده کنید
                "timestamp": None,
            },
        }
        return response

    if isinstance(exc, Http404):
        logger.warning(f"404 not found: {context['request'].path}")
        return Response(
            {
                "success": False,
                "code": 404,
                "message": "منبع مورد نظر یافت نشد",
                "data": None,
                "details": None,
                "meta": {"request_id": "unknown", "timestamp": None},
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, PermissionDenied):
        logger.warning(f"403 Forbidden: {context['request'].path}")
        return Response(
            {
                "success": False,
                "code": 403,
                "message": "شما اجازه دسترسی به این عملیات را ندارید",
                "data": None,
                "details": None,
                "meta": {"request_id": "unknown", "timestamp": None},
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, ValidationError):
        logger.warning(f"Validation Error: {str(exc)}")
        error_details = []
        for field, errors in exc.detail.items():
            for error in errors:
                error_details.append({"field": field, "error": str(error)})

        return Response(
            {
                "success": False,
                "code": 400,
                "message": "داده‌های ورودی معتبر نیست",
                "data": None,
                "details": error_details,
                "meta": {"request_id": "unknown", "timestamp": None},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    logger.exception(f"Internal Server Error: {str(exc)}")
    return Response(
        {
            "success": False,
            "code": 500,
            "message": "خطای سرور پیش آمد، لطفاً پس از مدت کوتاهی مجدداً تلاش نمایید",
            "data": None,
            "details": None,
            "meta": {"request_id": "unknown", "timestamp": None},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
