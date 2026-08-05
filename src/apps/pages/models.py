from django.db import models
from apps.core.models import BaseModel


class NewsletterSubscriber(BaseModel):
    email = models.EmailField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.email

    class Meta:
        verbose_name = "مشترک خبرنامه"
        verbose_name_plural = "مشترکین خبرنامه "


class FaqGroup(BaseModel):
    title = models.TextField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "گروه سوالات متداول"
        verbose_name_plural = "گروه های سوالات متداول"


class Faq(BaseModel):
    question = models.TextField(max_length=1024)
    answer = models.TextField(max_length=1024)
    group = models.OneToOneField(
        FaqGroup, on_delete=models.CASCADE, related_name="group"
    )

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"


class ContactUsSubject(BaseModel):
    title = models.TextField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "موضوع تماس با ما"
        verbose_name_plural = "موضوع های تماس با ما"


class ContactUs(BaseModel):
    subject = models.OneToOneField(ContactUsSubject, on_delete=models.CASCADE)
    fullname = models.TextField(max_length=255)
    message = models.TextField(max_length=255)
    mobile = models.TextField(max_length=255)

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "تماس با ما"
        verbose_name_plural = "تماس با ما ها"
