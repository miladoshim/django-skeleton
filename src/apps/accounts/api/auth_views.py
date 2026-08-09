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
