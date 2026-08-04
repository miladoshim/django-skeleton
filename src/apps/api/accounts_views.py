import jwt
from datetime import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from apps.academy.models import Enrollment
from apps.academy.serializers import UserAccountEnrollmentSerializer
from apps.accounts.models import User, UserBank
from apps.accounts.serializers import (
    UserAddressSerializer,
    UserBankSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from apps.api.renderers import CommonRenderer, UserRenderer
from apps.financial.models import CoachIncome, Payout


######## Start Dashboard Api ############
class AccountBankView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user


######## End Dashboard Api ############


class UserBankViewSet(ReadOnlyModelViewSet):
    """
    Return a list of all brands
    """

    queryset = UserBank.objects.all()
    serializer_class = UserBankSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [CommonRenderer]

    @method_decorator(cache_page(60 * 15, key_prefix="shop_brand_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserAddressViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressSerializer


class UserEnrollmentAPIView(ListAPIView):
    serializer_class = UserAccountEnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)


class WalletCharge(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.POST.get("amount")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggleFollow(request):
    try:
        try:
            user = User.objects.get(username=request.user.username)
            user_to_follow = User.objects.get(username=request.data["username"])
        except User.DoesNotExist:
            return Response({"error": "user does not exists"})

        if user in user_to_follow.followers.all():
            user_to_follow.followers.remove(user)
            return Response({"now_following": False})
        else:
            user_to_follow.followers.add(user)
            return Response({"now_following": True})
    except:
        return Response({"error": "error following"})


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def toggleLike(request):
#     try:
#         try:
#             post = Post.objects.get(id=request.data["id"])
#         except Post.DoesNotExist:
#             return Response({"error": "post does not exists"})

#         try:
#             user = User.objects.get(username=request.data["username"])
#         except User.DoesNotExist:
#             return Response({"error": "user does not exists"})

#         if user in post.likes.all():
#             post.likes.remove(user)
#             return Response({"now_liked": False})
#         else:
#             post.likes.add(user)
#             return Response({"now_liked": True})
#     except:
#         return Response({"error": "error like post"})


@permission_classes([IsAuthenticatedOrReadOnly])
@api_view(["GET"])
def get_user_profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "user does not exists"},
            status=status.HTTP_404_NOT_FOUND,
            exception=True,
        )

    serializer = UserSerializer(user, many=False, context={"request": request})

    # following = False
    # if request.user in user.followers.all():
    #     following = True

    return Response(
        {
            "data": serializer.data,
            "is_out_profile": request.user.username == user.username,
            # "following": following,
        }
    )


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("unauthenticated")

        try:
            payload = jwt.decode(token, "secret", algorithm="HS256")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("un authenticate")

        user = User.objects.get(id=payload["id"])
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def user_profile_update(request):
    data = request.data
    try:
        user = User.objects.get(username=request.data["username"])
    except User.DoesNotExist:
        return Response({"error": "user does not exists"})

    serializer = UserProfileSerializer(user, data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({**serializer.data, "success": True})
    return Response({**serializer.error, "success": False})


# class UserChangePasswordAPIView(APIView):
# renderer_classes = [UserRenderer]
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


class VipPlansListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        plans = list_all_plans()
        data = [
            {
                "id": p.id,
                "title": p.title,
                "price": p.price,
                "duration_days": p.duration_days,
                "max_free_courses_per_month": p.max_free_courses_per_month,
                "min_course_price_for_free": p.min_course_price_for_free,
                "level": p.level,
                "features": p.features,
            }
            for p in plans
        ]
        return Response(data)


class VipStatusAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vip = request.user.vip_subscriptions.filter(
            is_active=True, end_at__gte=timezone.now()
        ).first()

        if not vip:
            return Response({"is_vip": False})

        return Response(
            {
                "is_vip": True,
                "plan": vip.plan.title,
                "end_at": vip.end_at,
                "features": vip.plan.features,
            }
        )


class UpgradeVipPlanAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_plan_id = request.data.get("new_plan_id")

        try:
            new_plan = VipPlan.objects.get(id=new_plan_id)
        except VipPlan.DoesNotExist:
            return Response(
                {"error": "invalid plan id"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            upgrade_vip_plan(user, new_plan)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response({"success": True})


# class PurchaseVipPlanAPI(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         plan_id = request.data.get('plan_id')

#         plan = get_object_or_404(VipPlan, id=plan_id)

#         payment = Payment.objects.create( type=Payment.TYPE_VIP, user=user, vip_plan=plan, amount=plan.price, ref_id="TEMP",
#         # بعد از برگشت از درگاه آپدیت می‌کنی )
#         payment.save()

#         try:
#             purchase_vip_plan(user, plan)
#         except PermissionDenied as e:
#             return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

#         return Response({"success": True})


######## Coach Api ##############

# class InstructorRevenueAPI(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         instructor = request.user
#         total = get_total_revenue(instructor)
#         last_30_days = get_revenue_in_period(
#             instructor, timezone.now() - timedelta(days=30), timezone.now()
#         )
#         return Response(
#             {
#                 "total_revenue": total,
#                 "last_30_days": last_30_days,
#             }
#         )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_payout(request):
    coach = request.user.coach  # فرض بر وجود آبجکت Coach مرتبط

    # دریافت اطلاعات بانک
    account_number = request.data.get("ibans")  # یا شماره کارت
    amount = Decimal(request.data.get("amount"))

    if amount <= 0:
        return Response({"error": "مبلغ باید مثبت باشد"}, status=400)

    # چک کردن موجودی قابل برداشت
    available_balance = (
        CoachIncome.objects.filter(coach=coach, status=RevenueStatus.READY).aggregate(
            total=models.Sum("coach_share_amount")
        )["total"]
        or 0
    )

    if amount > available_balance:
        return Response(
            {
                "error": "موجودی کافی برای تسویه نیست.",
                "available": str(available_balance),
            },
            status=400,
        )

    # ایجاد درخواست تسویه
    try:
        with transaction.atomic():
            # قفل کردن سطوح (برای جلوگیری از دو درخواست همزمان)
            coach_incomes = CoachIncome.objects.filter(
                coach=coach, status=RevenueStatus.READY
            ).select_for_update()

            # جمع کردن موجودی تا سقف مبلغ درخواستی و قفل کردن آنها
            total_locked = Decimal(0)
            locked_incomes = []
            for income in coach_incomes:
                if total_locked + income.coach_share_amount >= amount:
                    break
                locked_incomes.append(income)
                total_locked += income.coach_share_amount

            if total_locked < amount:
                # اگر موجودی کم شد (رقابت با دیگران)
                return Response(
                    {"error": "موجودی در حین درخواست تغییر کرد."}, status=400
                )

            # ایجاد رکورد تسویه
            payout = Payout.objects.create(
                coach=coach,
                amount=amount,
                bank_account=account_number,  # یا شبا
                status=PayoutStatus.PENDING,
            )

            # تغییر وضعیت درآمدهای قفل شده
            CoachIncome.objects.filter(
                id__in=[inc.id for inc in locked_incomes]
            ).update(
                status=RevenueStatus.LOCKED
            )  # یا یک وضعیت جدید مثل WITHDRAWN_PENDING

            return Response(
                {
                    "message": "درخواست تسویه ثبت شد و در صف پردازش قرار گرفت.",
                    "payout_id": payout.id,
                    "status": payout.status,
                },
                status=201,
            )

    except DatabaseError:
        return Response({"error": "خطای داخلی سرور"}, status=500)


# views.py
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def coach_dashboard_stats(request):
    coach = request.user.coach

    available = (
        CoachIncome.objects.filter(coach=coach, status=RevenueStatus.READY).aggregate(
            total=models.Sum("coach_share_amount")
        )["total"]
        or 0
    )

    locked = (
        CoachIncome.objects.filter(coach=coach, status=RevenueStatus.LOCKED).aggregate(
            total=models.Sum("coach_share_amount")
        )["total"]
        or 0
    )

    total_earned = (
        CoachIncome.objects.filter(coach=coach).aggregate(
            total=models.Sum("coach_share_amount")
        )["total"]
        or 0
    )

    recent_payouts = Payout.objects.filter(coach=coach).order_by("-created_at")[:5]

    return Response(
        {
            "summary": {
                "total_earnings": str(total_earned),
                "available_for_withdraw": str(available),
                "pending_earnings": str(locked),
            },
            "recent_payouts": [
                {
                    "id": p.id,
                    "amount": str(p.amount),
                    "status": p.get_status_display(),
                    "date": p.created_at,
                    "message": p.error_message,
                }
                for p in recent_payouts
            ],
        }
    )
