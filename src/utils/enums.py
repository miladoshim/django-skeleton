from django.db.models import IntegerChoices


class UserRole(IntegerChoices):
    USER = 1, "کاربر معمولی"


class PublishStatusChoice(IntegerChoices):
    PUBLISHED = 1, "منتشر شده"
    DRAFT = 2, "پیش نویس"


class GenderChoices(IntegerChoices):
    MALE = 1, "آقا"
    FEMALE = 2, "خانم"
    __empty__ = "نامشخص"
