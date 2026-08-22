from apps.financial.services.wallet_service import WalletService
from utils.logger import logger
import os
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
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
from apps.financial.services.payment_service import PaymentService
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
        result = FollowService(request.user).toggle_follow(uuid)

        if result["success"]:
            messages.success(request, result["message"])
        else:
            messages.error(request, result["message"])

        return redirect(request.META.get("HTTP_REFERER", "/"))


class FollowersListView(View):
    template_name = "accounts/followers_list.html"

    def get(self, request, user_id):
        service = FollowService(request.user)
        result = service.get_followers(
            user_id,
            page=int(request.GET.get("page", 1)),
        )

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
        result = service.get_following(
            user_id,
            page=int(request.GET.get("page", 1)),
        )

        return render(
            request,
            self.template_name,
            {
                "following": result["items"],
                "pagination": result,
            },
        )


class WalletChargeView(LoginRequiredMixin, View):
    login_url = "apps.accounts:login_classic"

    def post(self, request):
        amount = int(request.POST.get("amount"))
        service = WalletService(request.user)
        result = service.validate_for_charge(amount)

        if result["success"]:
            callback_url = "apps.accounts:dashboard_financial_wallet_charge_callback"

            return PaymentService(
                request=request,
                amount=amount,
                payment_for=PaymentFor.WALLET_CHARGE,
                callback_url=callback_url,
            ).go_to_gateway()
        else:
            messages.error(request, result["message"])
            return redirect("apps.accounts:dashboard_financial")


class WalletChargeCallbackView(LoginRequiredMixin, View):
    login_url = "apps.accounts:login_classic"
    template_name = "financial/payment_result.html"

    def get(self, request):
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM)

        service = WalletService(request.user)
        result = service.process_callback(tracking_code)

        if result["success"]:
            return render(
                request,
                "financial/payment_result.html",
                {
                    "success": result["success"],
                    "message": result["message"],
                    "tc": result.get("tracking_code", tracking_code),
                    "btn_url": "apps.accounts:dashboard_financial",
                    "btn_title": "رفتن به کیف پول",
                },
            )
        else:
            return render(
                request,
                "financial/payment_result.html",
                {
                    "success": False,
                    "message": result["message"],
                    "tc": result.get("tracking_code", tracking_code),
                    "btn_url": "apps.accounts:dashboard_financial",
                    "btn_title": "رفتن به کیف پول",
                },
            )


# class CommentListView(LoginRequiredMixin, ListView):
#     context_object_name = "comments"
#     paginate_by = 24
#     template_name = "accounts/comments.html"

#     def get_queryset(self):
#         return Comment.objects.filter(user=self.request.user)
