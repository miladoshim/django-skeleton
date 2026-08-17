import logging
import os
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    DetailView,
    FormView,
    TemplateView,
)
from azbankgateways import (
    default_settings as settings,
)
from azbankgateways import (
    models as bank_models,
)
from apps.accounts.services.follow_service import FollowService
from apps.financial.services.payment_service import Payment as PaymentService
from apps.financial.models import (
    Payment,
    PaymentFor,
    WalletTransaction,
)
from apps.accounts.forms import (
    ChangePasswordForm,
    UserAccountEditForm,
)
from apps.accounts.models import (
    User,
)

####### Start Dashboard #############


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DashboardSettingView(LoginRequiredMixin, View):

    template_name = "accounts/setting.html"
    form_class = UserAccountEditForm
    success_url = reverse_lazy("apps.accounts:dashboard_setting")

    def get(self, request):
        return render(
            request,
            self.template_name,
            {"user": request.user},
        )

    @transaction.atomic
    def post(self, request):
        form = self.form_class(
            data=request.POST,
            files=request.FILES,
            user=request.user,
        )

        if form.is_valid():
            user = request.user
            user.username = form.cleaned_data["username"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]

            user.email = form.cleaned_data["email"]

            form_mobile = form.cleaned_data["mobile"]
            if user.mobile == form_mobile:
                pass
            elif User.objects.filter(mobile=form_mobile).exists():
                messages.info(request, f"کاربری با شماره {form_mobile} وجود دارد.")
            else:
                user.mobile = form_mobile
                user.meta.mobile_verified_at = None

            user.save()
            user.profile.bio = form.cleaned_data["bio"]
            avatar = form.cleaned_data.get("avatar")
            if avatar:
                self._save_avatar(user, avatar)
                user.profile.avatar = avatar

            user.profile.save()

            messages.success(request, "پروفایل با موفقیت ویرایش شد.")
            return HttpResponseRedirect(self.success_url)

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field} - {error}")

        return HttpResponseRedirect(self.success_url)

    def _save_avatar(self, user, avatar):

        if user.profile.avatar and user.profile.avatar != avatar:
            self._delete_old_avatar(user.profile.avatar.path)

        user.profile.avatar = avatar
        user.profile.save()

    def _delete_old_avatar(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


class DashboardChangePasswordView(LoginRequiredMixin, FormView):
    template_name = "accounts/change_password.html"
    form_class = ChangePasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_form"] = self.get_form()
        return context

    def form_valid(self, form):
        user = self.request.user

        if not user.check_password(form.cleaned_data["old_password"]):
            messages.error(self.request, "رمز عبور فعلی شما درست نیست")
            return self.form_invalid(form)

        user.set_password(form.cleaned_data["password"])
        user.save()

        messages.success(self.request, "رمز عبور شما با موفقیت تغییر کرد")
        return HttpResponseRedirect(
            reverse(
                "apps.accounts:dashboard_setting_password",
            )
        )

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field} - {error}")
        return super().form_invalid(form)


class UserProfileView(DetailView):
    model = User
    template_name = "accounts/profile/overview.html"
    context_object_name = "profile"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_queryset(self):
        return User.objects.filter(is_active=True)


class ToggleFollowView(LoginRequiredMixin, View):

    def post(self, request, uuid):
        service = FollowService(request.user)
        result = service.toggle_follow(uuid)

        if result["success"]:
            messages.success(request, result["message"])
        else:
            messages.error(request, result["message"])

        return redirect(request.META.get("HTTP_REFERER", "/"))


class FollowersListView(View):
    template_name = "accounts/followers_list.html"

    def get(self, request, user_id):
        service = FollowService(request.user)
        result = service.get_followers(user_id, page=int(request.GET.get("page", 1)))

        return render(
            request,
            self.template_name,
            {
                "followers": result["items"],
                "pagination": result,
            },
        )


class FollowingListView(View):
    template_name = "accounts/following_list.html"

    def get(self, request, user_id):
        service = FollowService(request.user)
        result = service.get_following(user_id, page=int(request.GET.get("page", 1)))

        return render(
            request,
            self.template_name,
            {
                "following": result["items"],
                "pagination": result,
            },
        )


# # @method_decorator(vary_on_cookie, name="dispatch")
# # @method_decorator(cache_page(60 * 15), name="dispatch")
# class CommentListView(LoginRequiredMixin, ListView):
#     context_object_name = "comments"
#     paginate_by = 24
#     template_name = "accounts/comments.html"

#     def get_queryset(self):
#         return Comment.objects.filter(user=self.request.user)


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


####### End Dashboard #############
