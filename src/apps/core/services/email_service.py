from django.core.mail import EmailMessage
from django.http import JsonResponse


def send_email(recipient_list: list, subject, message):
    headers = {"x-liara-tag": "test-tag"}  # Custom headers

    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=None,  # Uses MAIL_FROM from settings.py
            to=recipient_list,
            headers=headers,
        )
        email.send()
        return JsonResponse(
            {"status": "success", "message": "Email sent successfully!"}
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
