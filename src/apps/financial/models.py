from django.conf import settings
from django.db import models
from django.db import transaction
from auditlog.registry import auditlog
from azbankgateways.models import Bank
from apps.academy.models import Course
from apps.core.models import BaseModel
from utils.enums import UserRole

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


class IrBank(BaseModel):
    title = models.CharField(
        max_length=100,
        verbose_name="عنوان",
        unique=True,
    )
    logo = models.ImageField(
        upload_to="banks/",
        verbose_name="لوگو",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "بانک"
        verbose_name_plural = "بانک ها"

    def __str__(self):
        return self.title


class GiftCode(BaseModel):
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="عنوان کد هدیه",
    )
    code = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="کد",
        help_text="یک کد یکتا وارد کنید",
    )
    description = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="توضیحات",
        help_text="توضیحات در مورد مناسبت کد هدیه",
    )
    value = models.CharField(
        max_length=255,
        verbose_name="مقدار",
        help_text="مقدار شارژ کیف پول کاربر به تومان",
    )
    infinity = models.BooleanField(
        verbose_name="نامحدود",
        default=False,
        help_text="این کد به صورت نامحدود قابل استفاده باشد؟",
    )
    count_use = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد قابل استفاده",
    )
    used = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد استفاده شده",
    )

    class Meta:
        verbose_name = "کد هدیه"
        verbose_name_plural = "کد هدیه ها"

    def __str__(self):
        return self.code

    @property
    def can_use(self) -> bool:
        if self.infinity:
            return True

        if self.count_use == 0:
            return False
        else:
            return True

    def used_counter(self):
        self.used += 1
        if not self.infinity:
            self.count_use -= 1
        self.save()

    def create_user_used(self, user):
        UserGiftCodeUsed.objects.create(user=user, gift_code=self)

    def user_can_use(self, user):
        if UserGiftCodeUsed.objects.filter(user=user, gift_code=self).exists():
            return False
        return True

    def apply(self, user):
        try:
            with transaction.atomic():
                user.wallet.charge(self.value)

                self.used_counter()

                self.create_user_used(user)
                return True
        except:
            return False


class UserGiftCodeUsed(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="کاربر",
        help_text="کاربری که از کد هدیه استفاده کرده است",
        related_name="gift_codes_used",
    )
    gift_code = models.ForeignKey(
        GiftCode,
        on_delete=models.CASCADE,
        verbose_name="کد هدیه",
        help_text="کد هدیه که کاربر از آن استفاده کرده است",
        related_name="users_used",
    )
    used_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان استفاده",
        help_text="زمانی که کاربر از کد هدیه استفاده کرده است",
    )

    class Meta:
        verbose_name = "کد هدیه استفاده شده"
        verbose_name_plural = "کد های هدیه استفاده شده"

    def __str__(self):
        return f"{self.user.first_name} - {self.gift_code.title}"

    def is_used(self):
        return self.used_at is not None


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


class CoachIncomeStatus(models.IntegerChoices):
    PENDING = 1, "در انتظار تایید نهایی (دوره بازگشت وجه)"
    AVAILABLE = 2, "قابل برداشت "
    LOCKED = 3, "در انتظار پرداخت"
    WITHDRAWN = 4, "پرداخت شده"
    REFUNDED = 5, "بازگشت داده شده"  # این یعنی پول کسر شده


class CoachIncome(BaseModel):
    coach = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="مربی",
        related_name="incomes",
        limit_choices_to={"role": UserRole.COACH},
    )
    payment = models.ForeignKey(
        Payment,
        verbose_name="تراکنش مرتبط",
        on_delete=models.CASCADE,
        related_name="coach_incomes",
    )
    course = models.ForeignKey(
        Course,
        verbose_name="دوره",
        on_delete=models.CASCADE,
        related_name="coach_course_incomes",
    )
    course_amount = models.PositiveIntegerField()  # مبلغ دوره
    percent = models.PositiveIntegerField(default=40)  # درصد مربی در زمان خرید
    amount = models.PositiveIntegerField(null=True, blank=True)  # مبلغ کل درآمد
    status = models.PositiveSmallIntegerField(
        choices=CoachIncomeStatus.choices,
        default=CoachIncomeStatus.PENDING.value,
        verbose_name="وضعیت تسویه",
    )
    available_date = models.DateField(
        verbose_name="تاریخ قابل برداشت",
        null=True,
        help_text="تاریخی که مربی می‌تواند این مبلغ را برداشت کند",
    )
    locked_at = models.DateTimeField(null=True, blank=True)  # زمان قفل شدن
    withdrawn_at = models.DateTimeField(null=True, blank=True)  # زمان برداشت

    class Meta:
        verbose_name = "درآمد مربی"
        verbose_name_plural = "درآمدهای مربی"
        indexes = [
            models.Index(fields=["coach", "created_at"]),
            models.Index(fields=["course", "created_at"]),
            models.Index(fields=["payment", "created_at"]),
        ]

    def __str__(self):
        return f"{self.coach.first_name} - {self.course.title} - {self.amount} - {self.percent}%"

    def get_status_title(self):
        if self.status == CoachIncomeStatus.PENDING:
            return "در انتظار تایید"
        elif self.status == CoachIncomeStatus.AVAILABLE:
            return "قابل برداشت"
        elif self.status == CoachIncomeStatus.LOCKED:
            return "در انتظار پرداخت"
        elif self.status == CoachIncomeStatus.WITHDRAWN:
            return "پرداخت شده"
        elif self.status == CoachIncomeStatus.REFUNDED:
            return "برگشت داده شده"
        else:
            return "نا مشخص"


class PayoutStatus(models.IntegerChoices):
    PENDING = 1, "در انتظار تایید"
    PROCESSING = 2, "منتظر پرداخت بانکی"
    PAID = 3, "پرداخت شده"
    REJECTED = 4, "رد شده"
    FAILED = 5, "پرداخت ناموفق"


class Payout(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="مربی",
        related_name="payouts",
        limit_choices_to={"role": UserRole.COACH},
    )
    bank = models.ForeignKey(
        "accounts.UserBank",
        on_delete=models.CASCADE,
        verbose_name="حساب بانکی",
    )
    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ تسویه",
    )
    description = models.CharField(
        max_length=255,
        verbose_name="توضیحات مربی",
        null=True,
        blank=True,
    )
    status = models.PositiveSmallIntegerField(
        verbose_name="وضعیت",
        choices=PayoutStatus.choices,
        default=PayoutStatus.PENDING.value,
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تایید مدیریت",
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ رد تسویه",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ واریز به حساب مربی",
    )
    tracking_code = models.CharField(
        max_length=255,
        verbose_name="کد پیگیری",
        null=True,
        blank=True,
    )
    income_ids = models.JSONField(default=list, blank=True, null=True)

    # rejected_reason = models.TextField(
    #     null=True,
    #     blank=True,
    #     verbose_name="علت رد",
    # )
    # bank_transaction_id = models.CharField(
    #     max_length=100,
    #     blank=True,
    #     null=True,
    #     help_text="پاسخ سیستم بانکی",
    # )
    # processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "درخواست تسویه حساب"
        verbose_name_plural = "درخواست تسویه حساب ها"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"درخواست تسویه {self.user.get_full_name} - {self.amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValueError("مبلغ باید مثبت باشد")

    def clean_incomes(self):
        """بررسی اینکه آیا تمام درآمدهای ذخیره شده هنوز در دسترس هستند؟"""
        current_count = CoachIncome.objects.filter(
            id__in=self.income_ids,
            status=CoachIncomeStatus.LOCKED,
        ).count()
        return current_count > 0

    def get_status_title(self):
        if self.status == PayoutStatus.PENDING:
            return "در انتظار تایید"
        elif self.status == PayoutStatus.PROCESSING:
            return "منتظر پرداخت بانکی"
        elif self.status == PayoutStatus.PAID:
            return "پرداخت شده"
        elif self.status == PayoutStatus.REJECTED:
            return "رد شده"
        elif self.status == PayoutStatus.FAILED:
            return "پرداخت ناموفق"
        else:
            return "نا مشخص"


auditlog.register(Payment, serialize_data=True)
auditlog.register(GiftCode, serialize_data=True)
auditlog.register(UserGiftCodeUsed, serialize_data=True)
auditlog.register(Wallet, serialize_data=True)
auditlog.register(WalletTransaction, serialize_data=True)
auditlog.register(CoachIncome, serialize_data=True)
auditlog.register(Payout, serialize_data=True)
