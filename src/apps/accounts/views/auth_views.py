import datetime
import uuid
import logging
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
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
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
)
from django.contrib.auth.views import (
    PasswordChangeView as BasePasswordChangeView,
)
from django.contrib.auth.views import (
    PasswordResetView as BasePasswordResetView,
)
from celery.result import AsyncResult
from apps.accounts.forms import (
    ClassicLoginForm,
    ResetPasswordMobileForm,
    UserOtpCompleteForm,
    UserOtpForm,
    UserOtpVerifyForm,
)
from apps.accounts.services.social_auth__service import SocialAuthService
from apps.accounts.tasks import send_otp_password
from apps.accounts.models import OtpRequest, SocialAccount, User
from utils.decorators import anonymous_required
from utils.mixins import IsUnAuthenticatedMixin

logger = logging.getLogger(__name__)


class UserClassicRegisterView(TemplateView):
    template_name = "registration/register.html"


class UserOTPRegisterRequestView(TemplateView):
    template_name = "registration/otp_request.html"


class UserOTPRegisterVerifyView(TemplateView):
    template_name = "registration/otp_verify.html"


class ForgotPasswordView(TemplateView):
    template_name = "registration/forgot_password.html"


@anonymous_required("apps.pages:home_view")
def user_register_otp(request):
    if request.method == "POST":
        form = UserOtpForm(data=request.POST)
        if form.is_valid():
            mobile = form.cleaned_data["mobile"]
            user = User.objects.filter(mobile=mobile, is_active=True).exists()
            if user:
                messages.error(
                    request, "همچین شماره ای ثبت نام کرده است لطفا وارد شوید"
                )
            else:
                with transaction.atomic():
                    user = User.objects.update_or_create(mobile=mobile)

                    otp_data = {
                        "channel": "p",
                        "receiver": mobile,
                    }
                    otp = OtpRequest.objects.generate_otp(otp_data)

                    task_id = send_otp_password.apply_async(
                        kwargs={"receiver": mobile, "otp": otp.password}
                    )
                    result = AsyncResult(task_id)

                    if result.status == "PENDING" or result.status == "SUCCESS":

                        messages.success(request, "کد یک بار مصرف برای شما ارسال شد")
                        return HttpResponseRedirect(
                            reverse(
                                "apps.accounts:register_otp_verify_view",
                                kwargs={"mobile": mobile, "reqid": otp.request_id},
                            )
                        )
                    else:
                        messages.error(
                            request, f"خطا در ارسال کدیک بار مصرف {str(result)}"
                        )

        else:
            for key, error in list(form.errors.items()):
                messages.error(request, error)
    else:
        form = UserOtpForm
    return render(request, "registration/register_otp.html", {"form": form})


@anonymous_required("apps.pages:home_view")
def user_register_otp_verify(request, *args, **kwargs):
    mobile = kwargs.get("mobile")
    request_id = kwargs.get("reqid")
    if request.method == "POST":
        form = UserOtpVerifyForm(data=request.POST)
        if form.is_valid():
            code = form.data.get("code")

            if OtpRequest.objects.is_valid(
                receiver=mobile,
                request_id=request_id,
                password=code,
            ):
                messages.success(request, "ثبت نام خود را تکمیل کنید")
                return HttpResponseRedirect(
                    reverse(
                        "apps.accounts:register_otp_complete_view",
                        kwargs={"mobile": mobile, "reqid": request_id},
                    )
                )
            else:
                messages.error(request, "کد تایید وارد شده صحیح نمی باشد.")
        else:
            for key, error in list(form.errors.items()):
                messages.error(request, error)
    else:
        if not OtpRequest.objects.filter(receiver=mobile).exists():
            messages.error(request, "همچین شماره ای ثبت نام نکرده است")
        form = UserOtpVerifyForm

    context = {"form": form, "mobile": mobile, "request_id": request_id}
    return render(request, "registration/register_otp_verify.html", context=context)


def user_register_otp_complete(request, *args, **kwargs):
    if request.method == "POST":
        form = UserOtpCompleteForm(request.POST)
        if form.is_valid():
            receiver = form.data.get("receiver")
            reqid = form.data.get("request_id")
            first_name = form.data.get("first_name")
            last_name = form.data.get("last_name")
            password = form.data.get("password")

            with transaction.atomic():
                user = User.objects.filter(mobile=receiver).first()
                if not user:
                    messages.error(request, "همچین شماره موبایلی ثبت نام نکرده است")
                else:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_active = True
                    user.set_password(password)
                    user.save()
                    user.meta.mobile_verified_at = datetime.datetime.now()
                    user.meta.save()

                    OtpRequest.objects.filter(request_id=reqid).delete()

                    messages.success(request, "با موفقیت در کوکوند ثبت نام کردید")

                    return HttpResponseRedirect(reverse("apps.accounts:login_classic"))
        else:
            for key, error in list(form.errors.items()):
                messages.error(request, error)
    else:
        mobile = kwargs.get("mobile")
        request_id = kwargs.get("reqid")
        form = UserOtpCompleteForm
        context = {"form": form, "mobile": mobile, "request_id": request_id}

    return render(request, "registration/register_otp_complete.html", context=context)


class UserLoginView(IsUnAuthenticatedMixin, FormView):
    template_name = "registration/login.html"
    success_url = reverse_lazy("apps.pages:home_view")
    form_class = ClassicLoginForm

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(request=self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, "خوش آمدید.")
            return HttpResponseRedirect(self.success_url)
        else:
            messages.error(self.request, "نام کاربری یا رمز عبور اشتباه است")
            return HttpResponseRedirect(reverse("apps.accounts:login_classic"))

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
    @method_decorator(require_POST)  # فقط POST - امنتر
    def post(self, request):
        logout(request)
        messages.success(request, "از حساب کاربری خود خارج شدید.")
        return redirect(self.success_url)


@anonymous_required("apps.pages:home_view")
def forgot_password_mobile(request):
    if request.method == "POST":
        form = UserOtpForm(data=request.POST)
        if form.is_valid():
            mobile = form.data.get("mobile")
            user = User.objects.filter(mobile=mobile, is_active=True).first()
            if not user:
                messages.error(request, "همچین کاربری یافت نشد")
                return HttpResponseRedirect(
                    reverse("apps.accounts:password_forgot_mobile_view")
                )
            else:

                with transaction.atomic():

                    otp_data = {
                        "channel": "p",
                        "receiver": mobile,
                    }
                    otp = OtpRequest.objects.generate_otp(otp_data)

                    result = (
                        True  # Kavenegar.send_otp(receptor=mobile, otp=otp.password)
                    )
                    if result:
                        messages.success(request, "کد یک بار مصرف برای شما ارسال شد")

                        return HttpResponseRedirect(
                            reverse(
                                "apps.accounts:password_forgot_mobile_reset_view",
                                kwargs={"mobile": mobile, "reqid": otp.request_id},
                            )
                        )
                    else:
                        messages.error(request, "خطا در ارسال کدیک بار مصرف")
                        raise
        else:
            for key, error in list(form.errors.items()):
                messages.error(request, error)
    else:
        form = UserOtpForm
    return render(request, "registration/forgot_mobile.html", {"form": form})


@transaction.atomic
def forgot_password_mobile_reset(request, *args, **kwargs):
    if request.method == "POST":
        form = ResetPasswordMobileForm(request.POST)
        if form.is_valid():
            receiver = form.data.get("receiver")
            reqid = form.data.get("request_id")
            code = form.data.get("code")
            password = form.data.get("password")

            user = User.objects.filter(mobile=receiver, is_active=True).first()
            if not user:
                messages.error(request, "همچین کاربری یافت نشد")
                return HttpResponseRedirect(
                    reverse("apps.accounts:password_forgot_mobile_view")
                )

            if OtpRequest.objects.is_valid(
                receiver=receiver, request_id=reqid, password=code
            ):
                user.set_password(password)
                user.save()
                user.meta.password_changed_at = datetime.datetime.now()
                user.meta.save()

                OtpRequest.objects.filter(request_id=reqid).delete()

                messages.success(request, "رمز عبور شما با موفقیت تغییر کرد")

                return HttpResponseRedirect(reverse("apps.accounts:login_classic"))
            else:
                messages.error(request, "کد تایید وارد شده صحیح نمی باشد.")

        else:
            for key, error in list(form.errors.items()):
                messages.error(request, error)

    mobile = kwargs.get("mobile")
    request_id = kwargs.get("reqid")
    form = ResetPasswordMobileForm
    context = {"form": form, "mobile": mobile, "request_id": request_id}

    return render(request, "registration/forgot_mobile_reset.html", context=context)


class PasswordChangeView(IsUnAuthenticatedMixin, BasePasswordChangeView):
    pass


class PasswordChangeDoneView(TemplateView):
    pass


class PasswordResetView(BasePasswordResetView):
    success_url = reverse_lazy("apps.accounts:password_reset_done")


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
                user.meta.last_login_at = datetime.datetime.now()
                user.meta.save()

            # ========== دیباگ ==========
            print(f"User created: {user.id}")
            print(f"User active: {user.is_active}")
            # ========== دیباگ ==========

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # ========== دیباگ ==========
            print(f"After login, authenticated: {request.user.is_authenticated}")
            print(f"After login, user: {request.user.id}")
            print(f"Session keys: {request.session.keys()}")
            # ========== دیباگ ==========

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
