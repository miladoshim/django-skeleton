from django.contrib import messages
import logging
from django.http import JsonResponse
from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework import permissions, status
from apps.accounts.api.serializers import UserEmailRegisterSerializer
from apps.accounts.models import User
from apps.accounts.services.social_auth__service import SocialAuthService


# Classic Register with email/password
class UserEmailRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserEmailRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.save()

            return Response(
                {"message": "User registered successfully. OTP sent to your email."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserEmailRegisterSerializer
    queryset = User.objects.all()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutAPIView(APIView):
    """
    خروج از طریق API - مناسب برای Vue/React
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # دریافت refresh token از request
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # غیرفعال کردن توکن

            # اگر از JWT cookie استفاده میکنید
            response = Response(
                {"detail": "با موفقیت خارج شدید"}, status=status.HTTP_200_OK
            )

            # پاک کردن کوکیها
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response

        except Exception as e:
            return Response(
                {"detail": "خطا در خروج"}, status=status.HTTP_400_BAD_REQUEST
            )


# OTP Register with mobile : step one request otp code
def logout():
    pass


# OTP Register with mobile : step two verify otp code
def logout():
    pass


# OTP Register with mobile : step three complete register
def logout():
    pass


# Login with email/username/mobile/password
def logout():
    pass


# OTP Login or Register
def logout():
    pass


def logout():
    pass


class SocialLoginAPIView(APIView):
    """ورود از طریق API"""

    permission_classes = []

    def post(self, request, provider):
        code = request.data.get("code")

        try:
            service = SocialAuthService(provider, code)
            user, info = service.login()

            # ساخت توکن JWT
            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=400)


# ---------- API Views ----------


class SocialLoginAPIView(View):
    """
    ورود از طریق API (برای فرانت اند)
    POST /api/auth/social/{provider}/

    فرمت درخواست:
    {
        "code": "...",  # یا access_token
    }
    """

    def post(self, request, provider):
        import json

        try:
            body = json.loads(request.body)
            code = body.get("code")
            token = body.get("access_token")

            if not code and not token:
                return JsonResponse(
                    {"error": "code یا access_token الزامی است"}, status=400
                )

            # ورود با سرویس
            service = SocialAuthService(provider, code=code, token=token)
            user, info = service.login()

            # ساخت توکن JWT (اگر نیاز دارید)
            # from rest_framework_simplejwt.tokens import RefreshToken
            # refresh = RefreshToken.for_user(user)

            return JsonResponse(
                {
                    "success": True,
                    "user": {
                        "id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                }
            )

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"API login error: {str(e)}")
            return JsonResponse({"error": "خطای غیرمنتظره"}, status=500)
