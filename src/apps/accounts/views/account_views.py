import logging
from django.contrib import messages
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import (
    DetailView,
    FormView,
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


class DashboardSettingView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/setting.html"
    form_class = UserAccountEditForm
    model = User
    success_url = reverse_lazy("apps.dashboard:dashboard_setting")

    # def get_object(self, queryset):
    #     return User.objects.get(pk=self.request.user.pk)

    # def form_valid(self, form):
    #     return super().form_valid(form)

    # def form_invalid(self, form):
    #     return super().form_invalid(form)


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
    template_name = "accounts/profile.html"
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_queryset(self):
        return User.objects.filter(is_active=True)


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
