from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeView as BasePasswordChangeView,
    LoginView as BaseLoginView,
)
from django.contrib.auth import authenticate, login, logout, forms
from django.views.generic import TemplateView, CreateView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from apps.accounts.forms import ChangePasswordForm, UserRegisterForm, UserLoginForm
from .models import UserProfile, User
from utils.helpers import token_generator


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"


class AccountSettingView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/settings.html"
    model = User
    success_url = reverse_lazy("accounts")
    fields = ["username"]

    def get_object(self, queryset):
        return User.objects.get(pk=self.request.user.pk)


class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("accounts:login_view")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        try:
            user = User.objects.exclude(pk=self.instance.pk).get(email=email)
        except User.DoesNotExist:
            return email
        raise ValidationError(f"Email {email} is exists")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        current_site = get_current_site(self.request)
        mail_message = render_to_string(
            "accounts/account_verification_mail.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": token_generator.make_token(user),
            },
        )

        to_mail = form.cleaned_data.get("email")
        email = EmailMessage("subject", mail_message, to=to_mail)
        email.send()
        return HttpResponse("email sent")


class UserLoginView(BaseLoginView):
    template_name = "registration/login.html"
    success_url = reverse_lazy("blog:post_list")


def login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd["username"], password=cd["password"]
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("home_view")
                else:
                    return HttpResponse("account is not active")
            else:
                messages.info(request, "credentials invalid")
                return HttpResponse("credential is wrong")
    else:
        form = UserLoginForm()

    return render(request, "registration/login.html", {"form": form})


def activate_account_mail(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_encode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse("ok")
    else:
        return HttpResponse("link invalid")


class PasswordChangeView(BasePasswordChangeView):
    pass


class PasswordChangeDoneView(TemplateView):
    pass


def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if User.objects.filter(email=email).exits():
                messages.info(request, "email exists")
                return redirect("register_view")
            else:
                user = User.objects.create(email=email)
                user.save()

                login = auth.authenticate(email=email, password=password)
                auth.login(request, login)

                profile = UserProfile.objects.create(user=user)
                profile.save()

        else:
            messages.info(request, "Password not match")
            return redirect("register_view")

    else:
        return render(request, "registration/register.html")


@login_required(login_url="accounts:login_view")
def user_logout(request):
    logout(request)
    return redirect("blog:post_list")


@login_required(login_url="login_view")
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        user = request.user
        if form.is_valid():
            cd = form.cleaned_data
            old_password = cd["old_password"]
            password = cd["password"]
            password_confirmation = cd["password_confirmation"]
            if not user.check_password(old_password):
                return HttpResponse("رمز عبور فعلی شما درست نیست")
            elif password != password_confirmation:
                return HttpResponse("رمز عبور ها یکی نیستند")
            else:
                user.set_password(password)
                user.save()
                return HttpResponse("password changed")
        else:
            form = ChangePasswordForm()
        return render(request, "", {"form": form})
