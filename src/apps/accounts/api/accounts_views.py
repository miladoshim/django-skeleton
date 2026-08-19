from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    RetrieveAPIView,
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.accounts.models import User
from apps.accounts.api.serializers import (
    UserProfileSerializer,
    UserSerializer,
)
from apps.accounts.services.follow_service import FollowService


class UserProfileAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(User, username=self.request.POST.get("username"))


class ToggleFollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        service = FollowService(request.user)
        result = service.toggle_follow(user_id)

        return Response(result, status=status.HTTP_200_OK)


class FollowStatsAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        service = FollowService(request.user)
        result = service.get_stats(user_id)

        return Response(result)


class FollowStatusAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        service = FollowService(request.user)
        result = service.get_follow_status(user_id)

        return Response(result)


class FollowersListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        service = FollowService(request.user)
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 20))
        result = service.get_followers(user_id, page, limit)

        return Response(result)


class FollowingListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        service = FollowService(request.user)
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 20))
        result = service.get_following(user_id, page, limit)

        return Response(result)


class FollowSuggestionsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = FollowService(request.user)
        limit = int(request.query_params.get("limit", 10))
        result = service.get_suggestions(limit)

        return Response(result)


class WalletCharge(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.POST.get("amount")
        # service = WalletService(request.user ,amount)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("password")
        confirm_password = request.data.get("password_confirmation")

        if not user.check_password(old_password):
            return Response(
                {"detail": "رمز عبور فعلی اشتباه است"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"detail": "رمز عبورها یکسان نیستند"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 8:
            return Response(
                {"detail": "رمز عبور حداقل ۸ کاراکتر باید باشد"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # تغییر رمز
        user.set_password(new_password)
        user.save()

        # ارسال ایمیل اطلاعرسانی
        self._send_notification(user)

        return Response(
            {"detail": "رمز عبور با موفقیت تغییر کرد"}, status=status.HTTP_200_OK
        )

    def _send_notification(self, user):
        """ارسال ایمیل اطلاعرسانی"""
        send_mail(
            subject="تغییر رمز عبور",
            message=f"سلام {user.username}، رمز عبور شما با موفقیت تغییر کرد.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


# class UserChangePasswordAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, format=None):
#         serializer = UserChangePasswordSerializer(data=request.data)
#         context = {'user': request.user, 'msg': 'password changed'}
#         if serializer.is_valid(raise_exception=True):
#             return Response(context, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GetTokenView(APIView):
#     def post(self, request):
#         mobile = request.data.get('mobile')
#         code = request.data.get('code')
