from django.conf import settings
from django.db import models
from azbankgateways.models import Bank
from apps.core.models import BaseModel

User = settings.AUTH_USER_MODEL


class PaymentMethods(models.IntegerChoices):
    WALLET = 1, "پرداخت از کیف پول"
    ONLINE = 2, "پرداخت آنلاین"


class PaymentFor(models.IntegerChoices):
    WALLET_CHARGE = 1, "شارژ کیف پول"
    COURSE = 2, "خرید دوره"
    COACHING = 3, "ثبت نام در کوچینگ"
    SHOP = 4, "خرید از فروشگاه"
    PLUS = 5, "شارژ حساب پلاس"


class Payment(BaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="کاربر پرداخت کننده",
        related_name="payments",
    )
    tracking_code = models.CharField(
        max_length=255,
        verbose_name="کد پیگیری",
    )
    result = models.OneToOneField(
        Bank,
        on_delete=models.CASCADE,
        verbose_name="نتیجه درگاه پرداخت",
        related_name="result",
        blank=True,
        null=True,
    )
    final_amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ نهایی",
    )
    payment_method = models.PositiveSmallIntegerField(
        choices=PaymentMethods.choices,
        blank=True,
        default=PaymentMethods.ONLINE.value,
        verbose_name="روش پرداخت",
    )
    payment_for = models.PositiveSmallIntegerField(
        choices=PaymentFor.choices,
        verbose_name="دلیل پرداخت",
    )
    object_id_for = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    def get_for(self):
        if self.payment_for == PaymentFor.WALLET_CHARGE:
            return "شارژ کیف پول"
        elif self.payment_for == PaymentFor.COURSE:
            return "خرید دوره"
        elif self.payment_for == PaymentFor.COACHING:
            return "ثبت نام در کوچینگ"
        else:
            return "خرید از فروشگاه"

    def get_method(self):
        if self.payment_method == PaymentMethods.WALLET:
            return "از کیف پول"
        elif self.payment_method == PaymentMethods.ONLINE:
            return "پرداخت آنلاین"

    def get_status(self):
        if self.result is None:
            return "موفق و تکمیل شده"
        elif self.result.status == "WAITING":
            return "در حال انتظار"
        elif self.result.status == "REDIRECT_TO_BANK":
            return "به بانک هدایت شده"
        elif self.result.status == "RETURN_FROM_BANK":
            return "از بانک برگشت داده شده"
        elif self.result.status == "CANCEL_BY_USER":
            return "کنسل شده توسط کاربر"
        elif self.result.status == "EXPIRE_GATEWAY_TOKEN":
            return "EXPIRE_GATEWAY_TOKEN"
        elif self.result.status == "EXPIRE_VERIFY_PAYMENT":
            return "EXPIRE_VERIFY_PAYMENT"
        elif self.result.status == "COMPLETE" or self.result.status == "COMPLETED":
            return "موفق و تکمیل شده"
        else:
            return "نامشخص"

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت ها"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["result", "created_at"]),
        ]

    def __str__(self):
        return f"Payment by {self.user} amount {self.final_amount}"


class Wallet(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance = models.PositiveBigIntegerField(
        verbose_name="موجودی",
        default=0,
    )

    class Meta:
        verbose_name = "کیف پول"
        verbose_name_plural = "کیف پول ها"

    def __str__(self):
        return f"Wallet({self.user.id}) - {self.balance}"

    def charge(self, amount):
        self.balance += int(amount)
        self.save()

    def spend(self, amount: int):
        self.balance -= amount
        self.save()


class WalletTransaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["tracking_code"]),
            models.Index(fields=["user", "is_processed"]),
        ]
