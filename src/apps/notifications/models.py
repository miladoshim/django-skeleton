from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from django.contrib.auth.models import User

User = get_user_model()


class NotificationType(models.IntegerChoices):
    PUSH = 1, "پوش"
    EMAIL = 2, "ایمیل"
    SMS = 3, "اس ام اس"
    INAPP = 4, "اس ام اس"


class Notification(BaseModel):
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )

    message = models.TextField()
    is_read = models.BooleanField(default=False)
