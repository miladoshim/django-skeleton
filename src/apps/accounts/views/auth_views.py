import datetime
import re
import time
import uuid
import logging
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.db import transaction
from django.views.generic import FormView, TemplateView
from django.core.exceptions import ValidationError
from django.contrib.auth.views import (
    PasswordChangeView as BasePasswordChangeView,
)
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.views import (
    PasswordResetView as BasePasswordResetView,
)
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from celery.result import AsyncResult
from apps.accounts.forms import (
    ClassicLoginForm,
    ForgotPasswordForm,
    ForgotPasswordResetForm,
    ResetPasswordMobileForm,
    UserEmailRegisterForm,
    UserOtpCompleteForm,
    UserOtpForm,
    UserOtpVerifyForm,
)
from apps.accounts.services.auth_service import AuthService
from apps.accounts.services.social_auth__service import SocialAuthService
from apps.accounts.tasks import send_otp_password
from apps.accounts.models import OtpChannel, OtpRequest, SocialAccount, User
from utils.decorators import anonymous_required
from utils.mixins import IsUnAuthenticatedMixin
from utils.validators import validate_password_strength

logger = logging.getLogger(__name__)


class UserClassicRegisterView(IsUnAuthenticatedMixin, FormView):
    template_name = "registration/register.html"
    form_class = UserEmailRegisterForm
    success_url = reverse_lazy("apps.accounts:login_classic")

    def form_valid(self, form):
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        result = AuthService(request=self.request).register(
            first_name,
            last_name,
            email,
            password,
        )

        if result is None:
            messages.error(self.request, "خطای ناشناخته. لطفا دوباره تلاش کنید.")
            return redirect(reverse_lazy("apps.accounts:register_classic"))

        if result.get("success"):
            messages.success(self.request, result["message"])
            return redirect(self.success_url)
        else:
            messages.error(self.request, result["message"])
            return redirect(reverse_lazy("apps.accounts:register_classic"))

    def form_invalid(self, form):

        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)

        for field_name, errors in form.errors.items():
            for error in errors:
                field_label = (
                    form.fields[field_name].label
                    if field_name in form.fields
                    else field_name
                )
                messages.error(self.request, f"{field_label}: {error}")

        return super().form_invalid(form)


class EmailVerificationView(View):
    success_url = reverse_lazy("apps.accounts:login_classic")

    def get(self, request, uid, token):
        result = AuthService(self.request).verify_email(uid, token)
        if result:
            messages.success(request, "ایمیل شما تایید شد, لطفا وارد شوید.")
            return redirect(self.success_url)

        messages.error(request, "خطا در تایید ایمیل")
        return redirect(self.success_url)


class UserOTPRegisterRequestView(TemplateView):
    template_name = "registration/otp_request.html"


class UserOTPRegisterVerifyView(TemplateView):
    template_name = "registration/otp_verify.html"


@method_decorator(anonymous_required("apps.pages:home_view"), name="dispatch")
class UserRegisterOtpView(View):
    template_name = "registration/register_otp.html"
    form_class = UserOtpForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    @transaction.atomic
    def post(self, request):
        form = self.form_class(request.POST)

        if not form.is_valid():
            for error in form.errors.values():
                messages.error(request, error)
            return render(request, self.template_name, {"form": form})

        mobile = form.cleaned_data["mobile"]

        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, "این شماره قبلاً ثبت‌نام کرده است. لطفا وارد شوید.")
            return redirect("apps.accounts:login_classic")

        user, _ = User.objects.update_or_create(mobile=mobile)

        otp = OtpRequest.objects.generate_otp(
            {
                "channel": OtpChannel.MOBILE,
                "receiver": mobile,
            }
        )

        try:
            task = send_otp_password.apply_async(
                kwargs={"receiver": mobile, "otp": otp.password}
            )

            if task.status in ["PENDING", "SUCCESS"]:
                messages.success(request, "کد یکبار مصرف برای شما ارسال شد.")
                return redirect(
                    "apps.accounts:register_otp_verify_view",
                    mobile=mobile,
                    reqid=otp.request_id,
                    # kwargs={"mobile": mobile, "reqid": otp.request_id},
                )
            else:
                messages.error(
                    request, "خطا در ارسال کد یکبار مصرف. لطفا دوباره تلاش کنید."
                )

        except Exception as e:
            messages.error(request, f"خطا در ارسال کد: {str(e)}")

        return render(request, self.template_name, {"form": form})


class UserRegisterOtpVerifyView(View):
    template_name = "registration/register_otp_verify.html"
    form_class = UserOtpVerifyForm

    def get(self, request, mobile, reqid):
        if not OtpRequest.objects.filter(receiver=mobile).exists():
            messages.error(request, "شماره پیدا نشد.")
            return redirect("apps.accounts:register_otp_view")

        return self._render(request, mobile, reqid, self.form_class())

    def post(self, request, mobile, reqid):
        form = self.form_class(request.POST)

        if form.is_valid() and OtpRequest.objects.is_valid(
            receiver=mobile,
            request_id=reqid,
            password=form.cleaned_data["code"],
        ):
            messages.success(request, "کد تایید شد.")
            return redirect(
                "apps.accounts:register_otp_complete_view",
                mobile=mobile,
                reqid=reqid,
            )

        messages.error(request, "کد صحیح نیست.")
        return self._render(request, mobile, reqid, form)

    def _render(self, request, mobile, reqid, form):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "mobile": mobile,
                "request_id": reqid,
            },
        )


class UserRegisterOtpCompleteView(View):
    template_name = "registration/register_otp_complete.html"
    form_class = UserOtpCompleteForm

    def get(self, request, mobile, reqid):
        return render(
            request,
            self.template_name,
            {
                "form": self.form_class(),
                "mobile": mobile,
                "request_id": reqid,
            },
        )

    @transaction.atomic
    def post(self, request):
        form = self.form_class(request.POST)

        if not form.is_valid():
            for error in form.errors.values():
                messages.error(request, error)
            return render(request, self.template_name, {"form": form})

        user = User.objects.filter(mobile=form.cleaned_data["receiver"]).first()

        if not user:
            messages.error(request, "شماره موبایل پیدا نشد.")
            return redirect("apps.accounts:register_otp_view")

        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.is_active = True
        user.set_password(form.cleaned_data["password"])
        user.save()
        user.meta.mobile_verified_at = datetime.datetime.now()
        user.meta.save()

        OtpRequest.objects.filter(request_id=form.cleaned_data["request_id"]).delete()

        messages.success(request, "ثبت‌نام موفق بود.")

        return redirect("apps.accounts:login_classic")


class UserLoginView(IsUnAuthenticatedMixin, FormView):
    template_name = "registration/login.html"
    success_url = reverse_lazy("apps.pages:home_view")
    form_class = ClassicLoginForm

    def form_valid(self, form):
        identifier = form.cleaned_data.get("identifier")
        password = form.cleaned_data.get("password")

        service = AuthService(request=self.request)
        result = service.login(identifier, password)

        if result["success"]:
            if not self.request.user.is_authenticated:
                messages.error(self.request, "خطا در ورود")
                return redirect(reverse("apps.accounts:login_classic"))

            messages.success(self.request, "خوش آمدید!")
            return redirect(reverse("apps.pages:home_view"))

        messages.error(self.request, result["error"])
        return redirect(reverse("apps.accounts:login_classic"))

    def form_invalid(self, form):

        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)

        for field_name, errors in form.errors.items():
            for error in errors:
                field_label = (
                    form.fields[field_name].label
                    if field_name in form.fields
                    else field_name
                )
                messages.error(self.request, f"{field_label}: {error}")

        return super().form_invalid(form)


class UserLogoutView(LoginRequiredMixin, View):
    login_url = "apps.accounts:login_classic"
    success_url = reverse_lazy("apps.pages:home_view")

    @method_decorator(csrf_protect)
    @method_decorator(require_POST)
    def post(self, request):
        service = AuthService(request=self.request)
        result = service.logout()
        if result["success"]:
            messages.success(self.request, result["message"])
            return redirect(self.success_url)
        messages.error(self.request, result["error"])
        return redirect(self.success_url)


class ForgotPasswordView(IsUnAuthenticatedMixin, FormView):
    template_name = "registration/forgot_password.html"
    form_class = ForgotPasswordForm

    def form_valid(self, form):
        identifier = form.cleaned_data.get("identifier")
        result = AuthService(request=self.request).forgot_password(
            identifier=identifier
        )
        if result["success"]:
            messages.success(self.request, result["message"])
            return redirect(reverse(result["redirect_url"], args=[result['reqid']]))
        
        messages.error(self.request, result["message"])
        return redirect(reverse("apps.accounts:password_forgot_view"))

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        return self.render_to_response(self.get_context_data(form=form))

class ForgotPasswordDoneView(View):
    template_name = "registration/forgot_password_done.html"

    def get(self, request):
        return render(request, self.template_name)


class PasswordResetConfirmView(FormView):
    template_name = "registration/password_reset_confirm.html"
    form_class = ForgotPasswordResetForm
    success_url = reverse_lazy("apps.accounts:login_classic")

    def dispatch(self, request, *args, **kwargs):
        self.uid, self.token = kwargs.get("uid"), kwargs.get("token")

        if self.uid:
            result = AuthService(request=request).reset_password_confirm(
                self.uid, self.token
            )
            if not result["success"]:
                messages.error(request, result["error"])
                return redirect("apps.accounts:password_forgot_view")
            request.session["reset_user_id"] = force_str(
                urlsafe_base64_decode(self.uid)
            )

            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user_id = self.request.session.get("reset_user_id")
        if not user_id:
            return redirect("apps.accounts:password_forgot_view")

        result = AuthService(request=self.request).reset_password_confirm(
            self.uid, self.token, form.cleaned_data["password"]
        )

        if result["success"]:
            self.request.session.pop("reset_user_id", None)
            messages.success(self.request, result["message"])
            return super().form_valid(form)

        messages.error(self.request, result["error"])
        return self.form_invalid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
            return super().form_invalid(form)

    def _get_user(self, uid):
        try:
            return User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
        except:
            return None


class PasswordResetMobileConfirmView(FormView):
    template_name = "registration/forgot_password_mobile_verify.html"
    form_class = ResetPasswordMobileForm
    success_url = reverse_lazy("apps.accounts:login_view")

    def get_initial(self):
        return {
            "mobile": self.request.session.get("reset_mobile"),
            "reqid": self.request.session.get("reset_reqid"),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mobile"] = self.request.session.get("reset_mobile")
        context["reqid"] = self.request.session.get("reset_reqid")
        return context

    def form_valid(self, form):
        mobile = form.cleaned_data["mobile"]
        reqid = form.cleaned_data["reqid"]
        code = form.cleaned_data["code"]
        new_password = form.cleaned_data["password"]

        result = AuthService().verify_otp_and_reset_password(
            mobile=mobile,
            reqid=reqid,
            otp_code=code,
            new_password=new_password,
        )

        if result["success"]:
            self.request.session.pop("reset_mobile", None)
            self.request.session.pop("reset_reqid", None)

            messages.success(self.request, result["message"])
            return super().form_valid(form)

        messages.error(self.request, result["error"])
        return self.form_invalid(form)
    
    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        return self.render_to_response(self.get_context_data(form=form))


class ForgotPasswordMobileVerifyView(View):

    template_name = "registration/forgot_mobile_verify.html"

    def get(self, request):
        mobile = request.session.get("reset_mobile")

        if not mobile:
            messages.error(request, "لطفا ابتدا شماره موبایل را وارد کنید")
            return redirect("apps.accounts:password_forgot_view")

        return render(request, self.template_name, {"mobile": mobile})

    def post(self, request):
        mobile = request.session.get("reset_mobile")
        otp_code = request.POST.get("otp", "").strip()

        if not mobile:
            messages.error(request, "لطفا ابتدا شماره موبایل را وارد کنید")
            return redirect("apps.accounts:password_forgot_view")

        if not otp_code or len(otp_code) != 6:
            messages.error(request, "کد باید ۶ رقم باشد")
            return render(request, self.template_name)

        saved_otp = cache.get(f"otp_{mobile}")

        if saved_otp == otp_code:
            user = User.objects.filter(mobile=mobile).first()

            if not user:
                messages.error(request, "کاربر یافت نشد")
                return redirect("apps.accounts:password_forgot_view")

            cache.delete(f"otp_{mobile}")

            request.session["reset_user_id"] = str(user.id)
            request.session.pop("reset_mobile", None)

            return redirect("apps.accounts:password_forgot_mobile_reset_view")

        messages.error(request, "کد وارد شده اشتباه است")
        return render(request, self.template_name)


class ForgotPasswordMobileResetView(View):
    template_name = "registration/forgot_mobile_reset.html"

    def get(self, request):
        if not request.session.get("reset_user_id"):
            messages.error(request, "لطفا ابتدا کد را تایید کنید")
            return redirect("apps.accounts:password_forgot_view")

        return render(request, self.template_name)

    def post(self, request):
        user_id = request.session.get("reset_user_id")

        if not user_id:
            messages.error(request, "لطفا ابتدا کد را تایید کنید")
            return redirect("apps.accounts:password_forgot_view")

        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if password != confirm_password:
            messages.error(request, "رمزهای عبور یکسان نیستند")
            return render(request, self.template_name)

        try:
            validate_password_strength(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, self.template_name)

        try:
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()

            request.session.pop("reset_user_id", None)

            messages.success(
                request, "رمز عبور شما با موفقیت تغییر کرد. لطفا وارد شوید."
            )
            return redirect("apps.accounts:login_classic")

        except User.DoesNotExist:
            messages.error(request, "کاربر یافت نشد")
            request.session.pop("reset_user_id", None)
            return redirect("apps.accounts:password_forgot_view")


class ResendOtpView(View):
    """ارسال مجدد کد"""

    def get(self, request):
        mobile = request.session.get("reset_mobile")

        if not mobile:
            return redirect("apps.accounts:password_forgot_view")

        # محدودیت ارسال مجدد (هر 60 ثانیه)
        last_sent = cache.get(f"otp_sent_{mobile}")
        if last_sent and time.time() - last_sent < 60:
            messages.error(request, "لطفا 60 ثانیه صبر کنید.")
            return redirect("apps.accounts:password_forgot_mobile_verify_view")

        # ساخت کد جدید
        otp = str(random.randint(100000, 999999))
        cache.set(f"otp_{mobile}", otp, timeout=300)
        cache.set(f"otp_sent_{mobile}", time.time(), timeout=60)

        # ارسال SMS
        # Kavenegar.send_otp(receptor=mobile, otp=otp)

        messages.success(request, "کد جدید ارسال شد")
        return redirect("apps.accounts:password_forgot_mobile_verify_view")


def get_authorize_url(provider):
    urls = {
        "github": f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope=user:email",
        "google": f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&response_type=code&scope=openid email profile",
        "gitlab": f"https://gitlab.com/oauth/authorize?client_id={settings.GITLAB_CLIENT_ID}&redirect_uri={settings.GITLAB_REDIRECT_URI}&scope=read_user",
    }

    return urls.get(provider)


class SocialLoginView(View):

    def get(self, request, provider):
        try:
            state = str(uuid.uuid4())
            request.session["oauth_state"] = state
            request.session["oauth_provider"] = provider

            service = SocialAuthService(provider)
            url = service.get_authorize_url(state)

            return redirect(url)

        except ValueError as e:
            logger.error(f"Login error: {str(e)}")
            messages.error(request, f"خطا: {str(e)}")
            return redirect("apps.accounts:login_classic")


class SocialCallbackView(View):

    def get(self, request, provider):
        code = request.GET.get("code")
        state = request.GET.get("state")
        error = request.GET.get("error")

        if error:
            messages.error(request, f"ورود با {provider} لغو شد")
            return redirect("apps.accounts:login_classic")

        saved_state = request.session.get("oauth_state")
        saved_provider = request.session.get("oauth_provider")

        if provider != saved_provider or state != saved_state:
            messages.error(request, "خطای امنیتی: درخواست نامعتبر")
            return redirect("apps.accounts:login_classic")

        if not code:
            messages.error(request, "کد اعتبارسنجی دریافت نشد")
            return redirect("apps.accounts:login_classic")

        try:
            service = SocialAuthService(provider, code=code)
            user, info = service.login()

            if not user.is_active:
                user.is_active = True
                user.save()
            if not user.meta.email_verified_at:
                user.meta.email_verified_at = datetime.datetime.now()
                user.meta.save()

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            request.session.save()

            request.session.pop("oauth_state", None)
            request.session.pop("oauth_provider", None)

            messages.success(request, f"با موفقیت لاگین کردید!")

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)

            return redirect("apps.pages:home_view")

        except ValueError as e:
            logger.error(f"Callback error: {str(e)}")
            messages.error(request, f"خطا در ورود: {str(e)}")
            return redirect("apps.accounts:login_classic")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            messages.error(request, "خطای غیرمنتظره در ورود")
            return redirect("apps.accounts:login_classic")


class SocialAccountsListView(LoginRequiredMixin, View):

    template_name = "accounts/social_accounts.html"
    login_url = "apps.accounts:login_classic"

    def get(self, request):
        accounts = SocialAccount.objects.filter(user=request.user)

        context = {
            "accounts": accounts,
            "providers": ["github", "google", "gitlab"],
        }

        return render(request, self.template_name, context)


class SocialDisconnectView(LoginRequiredMixin, View):

    login_url = "apps.accounts:login_classic"

    def post(self, request, provider):
        try:
            service = SocialAuthService(provider)
            service.disconnect(request.user)

            messages.success(request, f"حساب {provider} با موفقیت قطع شد")
            return redirect("apps.accounts:social_accounts")

        except Exception as e:
            messages.error(request, f"خطا در قطع اتصال: {str(e)}")
            return redirect("apps.accounts:social_accounts")
