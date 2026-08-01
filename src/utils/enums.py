from django.db import models


class UserRole(models.IntegerChoices):
    STUDENT = 1, "دانشجو"
    COACH = 2, "مربی"


class Grades(models.IntegerChoices):
    A = 1, "دیپلم"
    B = 2, "کاردانی"
    C = 3, "کارشناسی"
    D = 4, "کارشناسی ارشد"
    E = 5, "دکتری "


class PublishStatusChoice(models.IntegerChoices):
    PUBLISHED = 1, "منتشر شده"
    DRAFT = 2, "پیش نویس"


class GenderChoices(models.IntegerChoices):
    MALE = 1, "آقا"
    FEMALE = 2, "خانم"
    __empty__ = "نامشخص"


class CourseStatusChoice(models.IntegerChoices):
    PLANNING = 1, "درحال برنامه ریزی"
    ONPROGRESS = 2, "درحال ضبط"
    COMPLETED = 3, "تکمیل شده"


class CourseLevelChoice(models.IntegerChoices):
    BEGINNING = 1, "مقدماتی"
    INTERMEDIATE = 2, "متوسط"
    ADVANCED = 3, "پیشرفته"


class PostTypeChoice(models.IntegerChoices):
    POST = 1, "بلاگ"
    PODCAST = 2, "پادکست"
    CINEMA = 3, "سینما"
