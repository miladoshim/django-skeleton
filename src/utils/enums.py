from django.db.models import IntegerChoices


class UserRole(IntegerChoices):
    USER = 1, "کاربر معمولی"


class PublishStatusChoice(IntegerChoices):
    PUBLISHED = 1, "منتشر شده"
    DRAFT = 2, "پیش نویس"


class GenderChoices(IntegerChoices):
    UNKNOWN = 1, "نامشخص"
    MALE = 2, "آقا"
    FEMALE = 3, "خانم"
