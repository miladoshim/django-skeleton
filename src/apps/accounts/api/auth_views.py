from django.http import JsonResponse
from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.api.permissions import IsNotAuthenticated
from apps.accounts.api.serializers import UserEmailRegisterSerializer
from apps.accounts.services.social_auth__service import SocialAuthService
from apps.accounts.services.auth_service import AuthService
from apps.api.renderers import CommonRenderer
from utils.logger import logger


class UserEmailRegisterView(APIView):
    """Classic Register with email/password"""

    permission_classes = (IsNotAuthenticated,)
    renderer_classes = (CommonRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = UserEmailRegisterSerializer(data=request.data)
        if serializer.is_valid():
            result = AuthService().register_email(
                serializer.data.get("first_name"),
                serializer.data.get("last_name"),
                serializer.data.get("email"),
                serializer.data.get("password"),
            )

            return Response(
                {"message": result["message"]},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    permission_classes = (IsNotAuthenticated,)

    def post(self, request):
        pass


class UserLogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            service = AuthService(request=request).logout()

            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response(
                {"detail": "با موفقیت خارج شدید"},
                status=status.HTTP_200_OK,
            )

            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response

        except Exception as e:
            return Response(
                {"detail": "خطا در خروج"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SocialLoginAPIView(View):

    def post(self, request, provider):
        try:
            code = request.POST.get("code")
            token = request.POST.get("access_token")

            if not code or not token:
                return JsonResponse(
                    {"error": "code یا access_token الزامی است"},
                    status=status.HTTP_400_BAD_REQUEST,
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
            return JsonResponse(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"API login error: {str(e)}")
            return JsonResponse(
                {"error": "خطای غیرمنتظره"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
