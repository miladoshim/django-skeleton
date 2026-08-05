from django.db import models


class UserRole(models.IntegerChoices):
    USER = 1, "کاربر معمولی"


class PublishStatusChoice(models.IntegerChoices):
    PUBLISHED = 1, "منتشر شده"
    DRAFT = 2, "پیش نویس"


class GenderChoices(models.IntegerChoices):
    MALE = 1, "آقا"
    FEMALE = 2, "خانم"
    __empty__ = "نامشخص"
