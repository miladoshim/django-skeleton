from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework import permissions, status
from apps.accounts.api.serializers import UserEmailRegisterSerializer
from apps.accounts.models import User


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
from rest_framework.permissions import IsAuthenticated
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
