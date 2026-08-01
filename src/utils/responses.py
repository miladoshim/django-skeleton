# utils/responses.py
import uuid
from typing import Any, Optional, Dict, List
from datetime import datetime
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status


class APIServiceResponse:

    @staticmethod
    def success(
        data: Any = None,
        message: str = "عملیات با موفقیت انجام شد",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict] = None,
    ) -> Response:

        response_data = {
            "success": True,
            "code": status_code,
            "message": message,
            "data": data,
            "meta": {
                "request_id": uuid.uuid4().hex,
                "timestamp": timezone.now().isoformat(),
            },
        }

        # اگر متادیتای اضافه‌ای (مثل Pagination) ارسال شده باشد، اضافه کن
        if meta:
            response_data["meta"].update(meta)

        return Response(response_data, status=status_code)

    @staticmethod
    def error(
        message: str,
        status_code: int,
        details: Optional[List[Dict]] = None,
        data: Any = None,
    ) -> Response:
        """
        ساخت پاسخ خطا
        """
        response_data = {
            "success": False,
            "code": status_code,
            "message": message,
            "data": data or [],  # اگر دیتایی برای نمایش جزئیات خطا وجود دارد
            "details": details or [],  # لیستی از خطاهای جزئی (مثلاً اعتبارسنجی فرم)
            "meta": {
                "request_id": uuid.uuid4().hex,
                "timestamp": timezone.now().isoformat(),
            },
        }

        return Response(response_data, status=status_code)

    @staticmethod
    def not_found(message: str = "منبع مورد نظر یافت نشد") -> Response:
        return APIServiceResponse.error(
            message=message, status_code=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def bad_request(message: str, details: List[Dict] = None) -> Response:
        return APIServiceResponse.error(
            message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details
        )

    @staticmethod
    def unauthorized(message: str = "توکن نامعتبر است") -> Response:
        return APIServiceResponse.error(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def internal_server_error(
        message: str = "خطای سرور پیش آمد، لطفاً بعداً دوباره تلاش کنید",
    ) -> Response:
        # لاگ کردن خطا در سمت سرور
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Internal Server Error: {message}")
        return APIServiceResponse.error(
            message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
