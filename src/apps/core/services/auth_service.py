from datetime import datetime
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail.message import EmailMessage
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from apps.accounts.admin import User


def send_activation_email(request, user):
    current_site = get_current_site(request)
    token = default_token_generator.make_token(user)
    encoded_uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_path = reverse("apps:accounts:activation", args=[encoded_uid, token])
    activation_url = f"{request.scheme}://{current_site}{activation_path}"
    print("----------------------Email Activation Url---------------------------")
    print(activation_url)
    message = render_to_string(
        "activation_email.html", {"user": user, "activation_url": activation_url}
    )
    email = EmailMessage("ایمیل خود را تایید کنید", message, to=[user.email])
    email.send()


def verify_activation_email(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        user.meta.update({"email_verified_at": datetime.now()})
        return True
    return False


def send_otp_sms(request, user):
    pass


def verify_otp_sms(request, user):
    pass


class TokenGenerator(PasswordResetTokenGenerator):
    pass


token_generator = TokenGenerator()
