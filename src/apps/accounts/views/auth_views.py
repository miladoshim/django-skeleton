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

        result = AuthService().register_email(first_name, last_name, email, password)

        messages.success(self.request, result["message"])

        return redirect(self.success_url)

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
        result = AuthService().verify_email(uid, token)
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
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        print(username, password)
        user = authenticate(request=self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, "خوش آمدید.")
            return redirect(self.success_url)
        else:
            messages.error(self.request, "نام کاربری یا رمز عبور اشتباه است")
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
    @method_decorator(require_POST)  # فقط POST - امنتر
    def post(self, request):
        logout(request)
        messages.success(request, "از حساب کاربری خود خارج شدید.")
        return redirect(self.success_url)


class ForgotPasswordView(IsUnAuthenticatedMixin, View):
    template_name = "registration/forgot_password.html"
    form_class = ForgotPasswordForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        identifier = request.POST.get("identifier", "").strip().lower()

        if not identifier:
            messages.error(request, "ایمیل یا موبایل را وارد کنید")
            return redirect("apps.accounts:password_forgot_view")

        if "@" in identifier:
            return self._handle_email(request, identifier)
        else:
            return self._handle_mobile(request, identifier)

    transaction.atomic

    def _handle_email(self, request, email):
        user = User.objects.filter(email__iexact=email).first()

        if not user:
            messages.error(request, "کاربری با این ایمیل یافت نشد")
            return redirect("apps.accounts:password_forgot_view")

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        reset_link = f"http://{domain}{reverse('apps.accounts:password_reset_confirm', kwargs={'uid': uid, 'token': token})}"

        try:
            send_mail(
                subject="بازیابی رمز عبور",
                message=f"""
                سلام {user.get_full_name}،

                برای بازیابی رمز عبور خود روی لینک زیر کلیک کنید:
                {reset_link}

                این لینک ۲۴ ساعت اعتبار دارد.
                اگر شما درخواست نداده‌اید، این ایمیل را نادیده بگیرید.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            messages.success(request, "لینک بازیابی به ایمیل شما ارسال شد")
            return redirect("apps.accounts:password_forgot_done_view")

        except Exception:
            messages.error(request, "خطا در ارسال ایمیل. لطفا بعدا تلاش کنید")
            return redirect("apps.accounts:password_forgot_view")

    @transaction.atomic
    def _handle_mobile(self, request, mobile):
        mobile = self._normalize_mobile(mobile)

        user = User.objects.filter(mobile=mobile, is_active=True).first()

        if not user:
            messages.error(request, "کاربری با این شماره یافت نشد")
            return redirect("apps.accounts:password_forgot_view")

        otp = OtpRequest.objects.generate_otp(
            {
                "channel": OtpChannel.MOBILE,
                "receiver": mobile,
            }
        )

        cache.set(f"otp_{mobile}", otp.password, timeout=300)

        try:
            task = send_otp_password.apply_async(
                kwargs={"receiver": mobile, "otp": otp.password},
            )

            if task.status in ["PENDING", "SUCCESS"]:
                messages.success(request, "کد یکبار مصرف برای شما ارسال شد.")
                return redirect(
                    reverse("apps.accounts:password_forgot_mobile_verify_view"),
                    mobile=mobile,
                    reqid=otp.request_id,
                )
            else:
                messages.error(
                    request, "خطا در ارسال کد یکبار مصرف. لطفا دوباره تلاش کنید."
                )

        except Exception as e:
            messages.error(request, f"خطا در ارسال کد: {str(e)}")
            print(str(e))

            return redirect("apps.accounts:password_forgot_view")

    def _normalize_mobile(self, mobile):
        mobile = re.sub(r"[^\d]", "", mobile)

        return mobile


class ForgotPasswordDoneView(View):
    template_name = "registration/forgot_password_done.html"

    def get(self, request):
        return render(request, self.template_name)


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


class PasswordResetConfirmView(View):
    template_name = "registration/password_reset_confirm.html"

    def get(self, request, uid, token):
        user = self._get_user(uid)

        if not user or not default_token_generator.check_token(user, token):
            messages.error(request, "لینک نامعتبر است")
            return redirect("apps.accounts:password_forgot_view")

        request.session["reset_user_id"] = str(user.id)
        return render(request, self.template_name)

    def post(self, request, uid, token):
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if not password or len(password) < 8:
            messages.error(request, "رمز حداقل ۸ کاراکتر")
            return render(request, self.template_name)

        if password != confirm:
            messages.error(request, "رمزها یکسان نیستند")
            return render(request, self.template_name)

        user_id = request.session.get("reset_user_id")
        if not user_id:
            return redirect("apps.accounts:password_forgot_view")

        with transaction.atomic():
            User.objects.filter(id=user_id).update(password=make_password(password))
            request.session.pop("reset_user_id", None)

        messages.success(request, "رمز شما تغییر کرد. وارد شوید.")
        return redirect("apps.accounts:login_view")

    def _get_user(self, uidb64):
        try:
            return User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
        except:
            return None


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
                return redirect(reverse("apps.accounts:password_forgot_mobile_view"))

            if OtpRequest.objects.is_valid(
                receiver=receiver, request_id=reqid, password=code
            ):
                user.set_password(password)
                user.save()
                user.meta.password_changed_at = datetime.datetime.now()
                user.meta.save()

                OtpRequest.objects.filter(request_id=reqid).delete()

                messages.success(request, "رمز عبور شما با موفقیت تغییر کرد")

                return redirect(reverse("apps.accounts:login_classic"))
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
