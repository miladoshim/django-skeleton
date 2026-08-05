import json
import logging
from django.contrib import messages
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models.aggregates import Sum
from django.urls import reverse, reverse_lazy
from django.db.models.base import ValidationError
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import (
    CreateView,
    ListView,
    TemplateView,
    UpdateView,
)
from azbankgateways import (
    default_settings as settings,
)
from azbankgateways import (
    models as bank_models,
)
from iranian_cities.models import Province
from apps.academy.models import Enrollment
from apps.coaching.models import Coaching
from apps.core.models import Bookmark, Comment
from apps.core.services.payment_service import Payment as PaymentService
from apps.financial.models import (
    CoachIncome,
    CoachIncomeStatus,
    GiftCode,
    IrBank,
    Payment,
    PaymentFor,
    Payout,
    WalletTransaction,
)
from apps.accounts.forms import (
    ChangePasswordForm,
    UserAccountEditForm,
    UserAddressForm,
    UserBankForm,
)
from apps.accounts.models import (
    User,
    UserBank,
)
from apps.financial.services import (
    create_coach_payout_request,
    get_available_coach_income_balance,
    get_available_coach_income_ids,
    get_paid_payouts,
    get_pending_payouts,
)
from apps.shop.models import Address, Order

####### Start Dashboard #############


@cache_page(60 * 15)
@vary_on_cookie
def user_profile(request, *args, **kwargs):
    user_uuid = kwargs.get("user_uuid")
    try:
        user = User.objects.get(uuid=user_uuid)
    except Exception as e:
        return HttpResponse("کاربر وجود ندارد")

    return render(request, "accounts/profile.html", {"user": user})


@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        form = UserAccountEditForm(
            data=request.POST or None,
            files=request.FILES or None,
        )

        if form.is_valid():
            with transaction.atomic():
                user.first_name = form.data.get("first_name")
                user.last_name = form.data.get("last_name")
                user.save()
                user.profile.bio = form.data.get("bio")
                user.profile.save()
                messages.success(request, "حساب کاربری ویرایش شد.")
                return HttpResponseRedirect(
                    reverse(
                        "apps.accounts:dashboard_setting",
                    )
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field} {error}")

            return HttpResponseRedirect(
                reverse(
                    "apps.accounts:dashboard_setting",
                )
            )
    else:
        return render(
            request,
            "accounts/setting.html",
            {
                "user": user,
            },
        )


@login_required
def change_password(request):
    if request.method == "POST":
        user = request.user
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.data.get("old_password")
            password = form.data.get("password")
            password_confirmation = form.data.get("password_confirmation")
            if not user.check_password(old_password):
                messages.error(request, "رمز عبور فعلی شما درست نیست")

            elif password != password_confirmation:
                messages.error(request, "رمز عبور ها یکی نیستند")

            else:
                user.set_password(password)
                user.save()
                # send notification to user
                messages.success(request, "رمز عبور شما تغییر کرد")
                return HttpResponseRedirect(
                    reverse(
                        "apps.accounts:login_view",
                    )
                )

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
                return HttpResponseRedirect(
                    reverse(
                        "apps.accounts:password_change",
                    )
                )
    else:
        form = ChangePasswordForm()
    return render(request, "accounts/change_password.html", {"password_form": form})


class DashboardSettingView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/setting.html"
    form_class = UserAccountEditForm
    model = User
    # success_url = reverse_lazy()

    def get_object(self, queryset):
        return User.objects.get(pk=self.request.user.pk)

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


# @method_decorator(vary_on_cookie, name="dispatch")
# @method_decorator(cache_page(60 * 15), name="dispatch")
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"
    login_url = reverse_lazy("apps.accounts:login_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["enrollment_count"] = self.request.user.enrollments.count
        context["coaching_count"] = self.request.user.coaching.count
        context["order_count"] = self.request.user.orders.count
        return context


# @method_decorator(vary_on_cookie, name="dispatch")
# @method_decorator(cache_page(60 * 15), name="dispatch")
class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/wishlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["books"] = Bookmark.objects.all()
        context["courses"] = Bookmark.objects.all()
        context["posts"] = Bookmark.objects.all()
        return context


class DashboardOrderView(LoginRequiredMixin, ListView):
    template_name = "accounts/orders.html"
    context_object_name = "orders"
    paginate_by = 24

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).all()


# @method_decorator(vary_on_cookie, name="dispatch")
# @method_decorator(cache_page(60 * 15), name="dispatch")
class DashboardCoachingView(LoginRequiredMixin, ListView):
    template_name = "accounts/coaching.html"
    context_object_name = "coaching"
    paginate_by = 24

    def get_queryset(self):
        return Coaching.objects.filter(user=self.request.user).all()


# @method_decorator(vary_on_cookie, name="dispatch")
# @method_decorator(cache_page(60 * 15), name="dispatch")
class CommentListView(LoginRequiredMixin, ListView):
    context_object_name = "comments"
    paginate_by = 24
    template_name = "accounts/comments.html"

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)


# @method_decorator(vary_on_cookie, name="dispatch")
# @method_decorator(cache_page(60 * 15), name="dispatch")
class EnrollmentListView(LoginRequiredMixin, ListView):
    template_name = "accounts/enrollments.html"
    context_object_name = "enrollments"

    def get_queryset(self):
        return (
            Enrollment.objects.filter(user=self.request.user)
            .prefetch_related("course")
            .all()
        )


# @method_decorator(vary_on_cookie, name="dispatch")
# @method_decorator(cache_page(60 * 15), name="dispatch")
class BankListView(LoginRequiredMixin, CreateView):
    template_name = "accounts/banks.html"
    form_class = UserBankForm
    success_url = reverse_lazy("apps.accounts:dashboard_banks")

    def get_queryset(self):
        return (
            UserBank.objects.filter(user=self.request.user)
            .select_related("bank")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["banks"] = UserBank.objects.filter(
            user=self.request.user
        ).select_related("bank")
        context["form"] = UserBankForm()
        context["irbanks"] = IrBank.objects.all().values("id", "title")
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "بانک با موفقیت اضافه شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


@require_http_methods(["GET"])
def detail_bank(request):
    bank_id = request.POST.get("bank_id")

    if bank_id is None:
        messages.error(request, "بانکی مشخص نشده است.")
        return redirect("apps.accounts:dashboard_banks")

    bank = get_object_or_404(UserBank, id=bank_id, user=request.user)
    return Response(bank)


@login_required
@require_http_methods(["POST", "PUT"])
def user_bank_update(request):
    bank_id = request.POST.get("bank_id")

    print(request.POST)
    if bank_id is None:
        messages.error(request, "بانک مورد نظر انتخاب نشده")
        return redirect("apps.accounts:dashboard_banks")

    try:
        bank = get_object_or_404(UserBank, id=bank_id, user=request.user)
        form = UserBankForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            messages.success(request, "بانک با موفقیت ویرایش شد")
            return redirect("apps.accounts:dashboard_banks")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)

            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field} {error}")
            return redirect("apps.accounts:dashboard_banks")
    except UserBank.DoesNotExist:
        messages.error(request, "حساب بانکی وجود ندارد")
        return redirect("apps.accounts:dashboard_banks")
    except Exception as e:
        messages.error(request, str(e))
        return redirect("apps.accounts:dashboard_banks")


@login_required
@require_http_methods(["POST", "DELETE"])
def user_bank_delete(request):
    bank_id = request.POST.get("bank_id")

    if bank_id is None:
        messages.error(request, "بانک مورد نظر انتخاب نشده")
        return redirect("apps.accounts:dashboard_banks")

    try:
        bank = get_object_or_404(UserBank, id=bank_id, user=request.user)
        bank.delete()
        messages.success(request, "حساب بانکی مورد نظر حذف شد ")
        return redirect("apps.accounts:dashboard_banks")
    except UserBank.DoesNotExist:
        messages.error(request, "حساب بانکی وجود ندارد")
        return redirect("apps.accounts:dashboard_banks")
    except Exception as e:
        messages.error(request, str(e))
        return redirect("apps.accounts:dashboard_banks")


def user_bank_api(request, pk=None):
    if request.method == "GET":
        if pk:
            note = get_object_or_404(UserBank, pk=pk)
            # تبدیل به دیکشنری JSON
            return JsonResponse(
                {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content,
                    "created_at": note.created_at.strftime("%Y-%m-%d"),
                }
            )
        else:
            # لیست تمام یادداشت‌ها
            data = list(UserBank.objects.values())
            return JsonResponse({"data": data}, safe=False)

    elif request.method in ["POST", "PUT"]:
        # دریافت داده JSON از درخواست
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "داده‌های نامعتبر"}, status=400
            )

        if pk:
            # آپدیت
            instance = get_object_or_404(UserBank, pk=pk)
            form = UserBankForm(data, instance=instance)
        else:
            # ایجاد جدید
            form = UserBankForm(data)

        if form.is_valid():
            form.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": f'یادداشت {"به‌روزرسانی" if pk else "ثبت"} شد.',
                    "id": form.instance.id,
                }
            )
        else:
            return JsonResponse(
                {"success": False, "errors": form.errors.as_json()}, status=400
            )

    elif request.method == "DELETE":
        try:
            note = get_object_or_404(UserBank, pk=pk)
            note.delete()
            return JsonResponse({"success": True, "message": "یادداشت حذف شد."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


# @method_decorator(vary_on_cookie, name="dispatch")
# @method_decorator(cache_page(60 * 15), name="dispatch")
class FinancialListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/financial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payments"] = Payment.objects.filter(
            user=self.request.user
        ).select_related("result")
        return context


@login_required
def wallet_gift_charge(request):
    if request.method == "POST":
        user = request.user
        code = request.POST.get("code")

        gift = GiftCode.objects.filter(code=code).first()
        if not gift:
            messages.error(request, "کد هدیه موجود نمی باشد")
            return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

        if not gift.user_can_use(user):
            messages.error(request, "شما قبلا از این کد هدیه استفاده کرده اید.")
            return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

        if not gift.can_use:
            messages.error(request, "کد هدیه قابل استفاده نمی باشد")
            return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

        if gift.apply(user):
            messages.success(request, "کیف پول شما شارژ شد.")
            return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))
        else:
            messages.error(request, "خطا در اعمال کد هدیه.")
            return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))


@login_required
def wallet_charge(request):
    if request.method == "POST":
        amount = int(request.POST.get("amount"))
        if amount < 100000:
            messages.error(request, "مبلغ کم تر از صد هزار تومان می باشد.")
            return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

        callback_url = "apps.accounts:dashboard_financial_wallet_charge_callback"
        pay = PaymentService(
            request=request,
            amount=amount,
            payment_for=PaymentFor.WALLET_CHARGE,
            callback_url=callback_url,
        )
        return pay.go_to_gateway()


@login_required
def wallet_charge_callback(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    with transaction.atomic():

        (
            wallet_transaction,
            created,
        ) = WalletTransaction.objects.select_for_update().get_or_create(
            tracking_code=tracking_code,
            defaults={
                "user": request.user,
                "amount": bank_record.amount,
                "is_processed": False,
            },
        )

        if wallet_transaction.is_processed:
            context = {
                "success": False,
                "message": "این تراکنش قبلا پردازش شده است.",
                "tc": tracking_code,
                "btn_url": "apps.accounts:dashboard_financial",
                "btn_title": "رفتن به کیف پول",
            }
            return render(request, "financial/payment_result.html", context=context)

        if bank_record.is_success:
            request.user.wallet.charge(bank_record.amount)

            wallet_transaction.is_processed = True
            wallet_transaction.processed_at = timezone.now()
            wallet_transaction.save()

            context = {
                "success": True,
                "message": f"کیف شما به مبلغ {bank_record.amount} شارژ شد",
                "tc": tracking_code,
                "btn_url": "apps.accounts:dashboard_financial",
                "btn_title": "رفتن به کیف پول",
            }
            return render(request, "financial/payment_result.html", context=context)

    context = {
        "success": False,
        "message": "پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.",
        "tc": tracking_code,
        "btn_url": "apps.accounts:dashboard_financial",
        "btn_title": "رفتن به کیف پول",
    }
    return render(request, "financial/payment_result.html", context=context)


class FinancialIncomeListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/incomes.html"

    def get_context_data(self, **kwargs):
        total_income = (
            CoachIncome.objects.filter(
                coach=self.request.user,
                status=CoachIncomeStatus.WITHDRAWN,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        total_income_month = (
            # , withdrawn_at__eq=datatme
            CoachIncome.objects.filter(
                coach=self.request.user,
                status=CoachIncomeStatus.WITHDRAWN,
            ).aggregate(total_month=Sum("amount"))["total_month"]
            or 0
        )
        context = super().get_context_data(**kwargs)
        context["banks"] = UserBank.objects.filter(
            user=self.request.user
        ).select_related("bank")
        context["incomes"] = CoachIncome.objects.filter(
            coach=self.request.user
        ).select_related("course")
        context["total_income"] = total_income
        context["total_income_month"] = total_income_month
        context["available_for_payout"] = get_available_coach_income_balance(
            self.request.user
        )
        return context


@login_required
# @user_passes_test(lambda u: u.is_coach)
def create_payout_request(request):
    try:
        user = request.user
        available_balance = get_available_coach_income_balance(user)

        income_for_payout_ids = get_available_coach_income_ids(user)

        print("---------------------------------------")
        print(income_for_payout_ids)
        print("---------------------------------------")
        print(available_balance)
        bank_id = request.POST.get("bank_id")

        bank = UserBank.objects.filter(id=bank_id).first()

        if available_balance < 1000000:
            messages.error(request, "مبلغ کم تر از یک میلیون تومان می باشد.")
            return HttpResponseRedirect(
                reverse("apps.accounts:dashboard_financial_incomes")
            )

        if not bank:
            messages.error(request, "همچین حساب بانکی وجود ندارد.")
            return HttpResponseRedirect(
                reverse("apps.accounts:dashboard_financial_incomes")
            )

        create_coach_payout_request(
            user,
            bank,
            available_balance,
            income_for_payout_ids,
        )

        messages.success(request, "درخواست تسویه حساب ثبت شد.")
        return HttpResponseRedirect(
            reverse("apps.accounts:dashboard_financial_payouts")
        )
    except ValidationError as e:
        messages.error(request, f"خطا در ثبت درخواست تسویه: {str(e)}")
        return HttpResponseRedirect(
            reverse("apps.accounts:dashboard_financial_incomes")
        )
    except Exception as e:
        messages.error(request, f"خطا در ثبت درخواست تسویه: {str(e)}")
        return HttpResponseRedirect(
            reverse("apps.accounts:dashboard_financial_incomes")
        )


class FinancialPayoutListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/payouts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payouts"] = Payout.objects.all
        context["paid_amount"] = get_paid_payouts(self.request.user)
        context["pending_amount"] = get_pending_payouts(self.request.user)
        return context


class AddressListView(LoginRequiredMixin, CreateView):
    template_name = "accounts/addresses.html"
    form_class = UserAddressForm
    success_url = reverse_lazy("apps.accounts:dashboard_addresses")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["provinces"] = Province.objects.all()
        context["addresses"] = (
            Address.objects.filter(user=self.request.user)
            .select_related("province", "city")
            .order_by("-created_at")
        )
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "آدرس با موفقیت اضافه شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field} {error}")
        return super().form_invalid(form)


@login_required
@require_http_methods(["POST", "PUT"])
def user_address_update(request):
    address_id = request.POST.get("address_id")

    if address_id is None:
        messages.error(request, "آدرس مورد نظر انتخاب نشده")
        return redirect("apps.accounts:dashboard_addresss")

    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        form = UserAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "آدرس با موفقیت ویرایش شد")
            return redirect("apps.accounts:dashboard_addresses")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field} {error}")
            return redirect("apps.accounts:dashboard_addresses")
    except Address.DoesNotExist:
        messages.error(request, "آدرس وجود ندارد")
        return redirect("apps.accounts:dashboard_addresses")
    except Exception as e:
        messages.error(request, str(e))
        return redirect("apps.accounts:dashboard_addresses")


@login_required
@require_http_methods(["POST", "DELETE"])
def user_address_delete(request):
    address_id = request.POST.get("address_id")

    if address_id is None:
        messages.error(request, "آدرس مورد نظر انتخاب نشده")
        return redirect("apps.accounts:dashboard_addresses")

    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()
        messages.success(request, "آدرس مورد نظر حذف شد ")
        return redirect("apps.accounts:dashboard_addresses")
    except Address.DoesNotExist:
        messages.error(request, "آدرس وجود ندارد")
        return redirect("apps.accounts:dashboard_addresses")
    except Exception as e:
        messages.error(request, str(e))
        return redirect("apps.accounts:dashboard_addresses")


def payout_dashboard(request):
    instructor = request.user
    if not instructor.is_staff:
        return redirect("home")

    # محاسبه موجودی قابل برداشت
    # 1. فقط درآمدهای قطعی (cleared)
    # 2. که تاریخشان گذشته است
    # 3. و هنوز در هیچ درخواست پرداختی ('paid') ثبت نشده‌اند
    # (برای سادگی، فرض می‌کنیم اگر درخواستی با وضعیت pending/approved باشد، آن مبلغ قفل می‌شود.
    #  اما برای دقت بیشتر، بهتر است مبلغ موجودی را بر اساس درآمد منهای درخواست‌های تایید نشده حساب کنید.)

    # روش ساده‌تر و ایمن‌تر:
    # موجودی کل = مجموع تمام درآمدهای cleared
    # منهای = مجموع مبالغ درخواست‌های approved یا paid

    total_earned = (
        CoachIncome.objects.filter(
            instructor=instructor,
            status="cleared",
            available_date__lte=timezone.now().date(),
        ).aggregate(total=Sum("share_amount"))["total"]
        or 0
    )

    total_pending_payouts = (
        Payout.objects.filter(
            instructor=instructor,
            status__in=["approved", "paid"],  # درخواست‌هایی که تایید شده‌اند
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    available_balance = total_earned - total_pending_payouts

    if request.method == "POST":
        amount_str = request.POST.get("amount")
        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            messages.error(request, "مبلغ نامعتبر است.")
            return redirect("payout_dashboard")

        if amount <= 0:
            messages.error(request, "مبلغ باید مثبت باشد.")
        elif amount > available_balance:
            messages.error(
                request,
                f"موجودی شما {available_balance} تومان است. مبلغ درخواستی نباید بیشتر باشد.",
            )
        else:
            # ایجاد درخواست
            PayoutRequest.objects.create(
                instructor=instructor, amount=amount, status="pending"
            )
            messages.success(
                request, "درخواست تسویه حساب شما ثبت شد و در صف بررسی است."
            )
            return redirect("payout_dashboard")

    context = {
        "available_balance": available_balance,
        "total_earned": total_earned,
        "pending_requests": PayoutRequest.objects.filter(
            instructor=instructor
        ).order_by("-created_at"),
    }
    return render(request, "instructors/payout_dashboard.html", context)


def instructor_payout_dashboard(request):

    # 2. محاسبه مبالغ درخواست شده که هنوز پرداخت نشده‌اند (Pending & Approved)
    # این مبلغ از موجودی کسر می‌شود تا از سرپوشان (Double Spending) جلوگیری شود
    total_pending_requests = (
        PayoutRequest.objects.filter(
            instructor=request.user, status__in=["pending", "approved"]
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    # موجودی قابل برداشت فعلی
    available_balance = total_cleared - total_pending_requests

    # 3. دریافت تاریخچه درخواست‌های تسویه
    payout_history = (
        PayoutRequest.objects.filter(instructor=request.user)
        .select_related("instructor")
        .order_by("-created_at")
    )

    context = {
        "available_balance": available_balance,
        "total_earned_cleared": total_cleared,
        "pending_requests": payout_history,
        "pending_amount": total_pending_requests,
    }
    return render(request, "instructors/payout_dashboard.html", context)


def request_payout(request):

    available_balance = None
    if request.method == "POST":
        amount_str = request.POST.get("amount")
        bank_account = request.POST.get("bank_account")

        if not amount_str:
            messages.error(request, "مبلغ را وارد کنید.")
            return redirect("instructor_payout_dashboard")

        try:
            amount = float(amount_str)
        except ValueError:
            messages.error(request, "فرمت مبلغ صحیح نیست.")
            return redirect("instructor_payout_dashboard")

        if amount <= 0:
            messages.error(request, "مبلغ باید مثبت باشد.")
            return redirect("instructor_payout_dashboard")

        # محاسبه مجدد موجودی قبل از ثبت
        today = timezone.now().date()
        total_cleared = (
            CoachIncome.objects.filter(
                instructor=request.user, status="cleared", available_date__lte=today
            ).aggregate(total=Sum("share_amount"))["total"]
            or 0
        )

        total_pending = (
            PayoutRequest.objects.filter(
                instructor=request.user, status__in=["pending", "approved"]
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        available_balance = total_cleared - total_pending

        if amount > available_balance:
            messages.error(
                request,
                f"موجودی شما کافی نیست. موجودی فعلی: {available_balance:,.0f} تومان",
            )
            return redirect("instructor_payout_dashboard")

        # ثبت درخواست
        PayoutRequest.objects.create(
            instructor=request.user,
            amount=amount,
            status="pending",
            notes=f"درخواست جدید به مبلغ {amount} (شماره حساب: {bank_account})",
        )
        messages.success(
            request,
            "درخواست تسویه حساب با موفقیت ثبت شد. پس از تایید ادمین پرداخت می‌شود.",
        )
        return redirect("instructor_payout_dashboard")

    return redirect("instructor_payout_dashboard")


def admin_financial_report(request):
    if not request.user.is_superuser:
        messages.error(request, "دسترسی غیرمجاز.")
        return redirect("home")

    today = timezone.now()

    # --- داده‌های کلیدی (KPIs) ---
    # 1. درآمد کل کسب شده (همه درآمدهای 'cleared')
    total_revenue = (
        CoachIncome.objects.filter(status="cleared").aggregate(
            total=Sum("share_amount")
        )["total"]
        or 0
    )

    # 2. درآمد قابل برداشت (موجودی تسویه نشده مربیان)
    # این یعنی درآمدهای 'cleared' که هنوز توسط هیچ پرتفوی تسویه‌ای پوشش داده نشده‌اند
    # (رویکرد ساده: کل درآمدهای cleared منهای کل پرداختی‌های تایید شده)
    total_paid_out = (
        PayoutRequest.objects.filter(status__in=["paid", "approved"]).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    pending_payouts = (
        total_revenue - total_paid_out
    )  # تقریبی، برای دقت بالا نیاز به کوئری پیچیده‌تر است

    # 3. آمار درخواست‌های تسویه
    payout_stats = PayoutRequest.objects.all().aggregate(
        count=Count("id"),
        pending=Count("id", filter=Q(status="pending")),
        paid=Count("id", filter=Q(status="paid")),
        rejected=Count("id", filter=Q(status="rejected")),
    )

    # --- گزارش درآمد ماهانه (گروپ‌بندی) ---
    # استفاده از TruncMonth برای دسته‌بندی خودکار ماه‌ها
    monthly_data = (
        CoachIncome.objects.filter(status="cleared")
        .annotate(month_start=TruncMonth("created_at"), month_total=Sum("share_amount"))
        .values("month_start", "month_total")
        .order_by("month_start")[:-6]
    )  # ۶ ماه آخر را نشان می‌دهد

    # --- گزارش درآمد بر اساس مربی (Top Instructors) ---
    top_instructors = (
        CoachIncome.objects.values("instructor__username", "instructor__email")
        .annotate(total_earned=Sum("share_amount"))
        .order_by("-total_earned")[:10]
    )

    # --- گزارش درآمدهای تسویه نشده (برای بررسی دقیق) ---
    # لیست مربیانی که درآمد دارند اما هنوز تسویه نشده‌اند
    # این نیازمند کوئری‌ای است که درآمد را با درخواست‌های تسویه مقایسه کند
    # به صورت ساده: مربیانی که درآمدهای 'cleared' دارند و مجموع درخواست‌هایشان < درآمدشان است

    context = {
        "total_revenue": total_revenue,
        "pending_payouts": pending_payouts,
        "payout_stats": payout_stats,
        "monthly_data": monthly_data,
        "top_instructors": top_instructors,
        "today": today,
    }

    return render(request, "admin/financial_reports.html", context)


# def recipes(request):
#     if request.method == 'POST':
#         data = request.POST
#         recipe_image = request.FILES.get('recipe_image')
#         recipe_name = data.get('recipe_name')
#         recipe_description = data.get('recipe_description')

#         Recipe.objects.create(
#             recipe_image=recipe_image,
#             recipe_name=recipe_name,
#             recipe_description=recipe_description,
#         )
#         return redirect('/')

#     queryset = Recipe.objects.all()
#     if request.GET.get('search'):
#         queryset = queryset.filter(recipe_name__icontains=request.GET.get('search'))
#     context = {'recipes': queryset}
#     return render(request, 'recipes.html', context)


# def delete_recipe(request, id):
#     recipe = get_object_or_404(Recipe, id=id)
#     recipe.delete()
#     return redirect('/')


# def update_recipe(request, id):
#     recipe = get_object_or_404(Recipe, id=id)
#     if request.method == 'POST':
#         data = request.POST
#         recipe_name = data.get('recipe_name')
#         recipe_description = data.get('recipe_description')
#         recipe_image = request.FILES.get('recipe_image')
#         recipe.recipe_name = recipe_name
#         recipe.recipe_description = recipe_description
#         if recipe_image:
#             recipe.recipe_image = recipe_image
#         recipe.save()
#         return redirect('/')
#     context = {'recipe': recipe}
#     return render(request, 'update_recipe.html', context)


# def orderFormView(request):
#     form = OrderForm()
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('show_url')
#     template_name = 'crudapp/order.html'
#     context = {'form': form}
#     return render(request, template_name, context)


# def updateView(request, f_oid):
#     obj = Orders.objects.get(oid=f_oid)
#     form = OrderForm(instance=obj)
#     if request.method == 'POST':
#         form = OrderForm(request.POST, instance=obj)
#         if form.is_valid():
#             form.save()
#             return redirect('show_url')
#     template_name = 'crudapp/order.html'
#     context = {'form': form}
#     return render(request, template_name, context)


# def deleteView(request, f_oid):
#     obj = Orders.objects.get(oid=f_oid)
#     if request.method == 'POST':
#         obj.delete()
#         return redirect('show_url')
#     template_name = 'crudapp/confirmation.html'
#     context = {'obj': obj}
#     return render(request, template_name, context)


####### End Dashboard #############
