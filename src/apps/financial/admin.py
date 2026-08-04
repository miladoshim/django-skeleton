from datetime import datetime
from django.utils.translation import ngettext
from django.contrib import admin, messages
from import_export.admin import ImportExportModelAdmin
from .models import (
    GiftCode,
    PayoutStatus,
    UserGiftCodeUsed,
    IrBank,
    Payment,
    Payout,
    CoachIncome,
)


@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    list_display = [
        "id",
        "user",
        "tracking_code",
        "final_amount",
        "payment_method",
        "payment_for",
        # "result__status",
    ]
    list_display_links = ["id", "user"]
    empty_value_display = "---"
    date_hierarchy = "created_at"
    search_fields = [
        "user",
    ]


@admin.register(Payout)
class PayoutAdmin(ImportExportModelAdmin):
    list_display = [
        "id",
        "user",
        "bank",
        "amount",
        "status",
        "paid_at",
        "rejected_at",
        "tracking_code",
        "created_at",
    ]
    list_display_links = ["id", "user"]
    empty_value_display = "---"
    date_hierarchy = "created_at"
    search_fields = ["user__mobile", "tracking_code"]
    list_filter = ["status", "user"]
    readonly_fields = [
        "amount",
        "paid_at",
        "rejected_at",
        "approved_at",
        "created_at",
        "tracking_code",
        "income_ids",
    ]
    list_select_related = (
        "user",
        "bank",
    )
    autocomplete_fields = ("user",)

    # actions = ["payout_approved", "payout_paid", "payout_rejected"]

    # @admin.action(description="تایید درخواست تسویه انتخاب شده")
    # def payout_approved(self, request, queryset):
    #     approved = queryset.update(
    #         status=PayoutStatus.PROCESSING,
    #         approved_at=datetime.now(),
    #     )
    #     self.message_user(
    #         request,
    #         ngettext(
    #             f"{approved} درخواست تسویه تایید شده.",
    #             f"{approved} درخواست تسویه تایید شدند",
    #             approved,
    #         ),
    #         messages.SUCCESS,
    #     )

    # def payout_rejected(self, request, queryset):
    #     rejected = queryset.update(
    #         status=PayoutStatus.REJECTED,
    #         approved_at=None,
    #         rejected_at=datetime.now(),
    #     )
    #     self.message_user(
    #         request,
    #         ngettext(
    #             f"{rejected} درخواست تسویه رد شده.",
    #             f"{rejected} درخواست تسویه رد شدند",
    #             rejected,
    #         ),
    #         messages.SUCCESS,
    #     )

    # def payout_paid(self, request, queryset):
    #     paid = queryset.update(
    #         status=PayoutStatus.PAID,
    #         paid_at=datetime.now(),
    #     )
    #     self.message_user(
    #         request,
    #         ngettext(
    #             f"{paid} درخواست تسویه پرداخت شده.",
    #             f"{paid} درخواست تسویه پرداخت شدند",
    #             paid,
    #         ),
    #         messages.SUCCESS,
    #     )

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(CoachIncome)
class CoachIncomeAdmin(ImportExportModelAdmin):
    list_display = [
        "id",
        "coach",
        "payment",
        "course",
        "course_amount",
        "percent",
        "amount",
        "status",
        "available_date",
    ]
    list_display_links = ["id", "coach", "payment"]
    empty_value_display = "---"
    date_hierarchy = "created_at"
    search_fields = ["coach__mobile", "course__title"]
    readonly_fields = ["coach", "course", "payment", "available_date"]
    list_editable = ["status"]

    def has_add_permission(self, request):
        return False


@admin.register(IrBank)
class IrBankAdmin(ImportExportModelAdmin):
    list_display = ["id", "title", "logo"]
    list_display_links = ["id", "title"]
    empty_value_display = "---"
    date_hierarchy = "created_at"
    search_fields = ["title"]


@admin.register(GiftCode)
class GiftcodeAdmin(ImportExportModelAdmin):
    list_display = [
        "id",
        "title",
        "code",
        "value",
        "infinity",
        "count_use",
        "used",
        "created_at",
    ]
    list_editable = ["value"]
    list_display_links = ["id", "title", "code"]
    empty_value_display = "---"
    date_hierarchy = "created_at"
    search_fields = ["title"]


@admin.register(UserGiftCodeUsed)
class UserGiftCodeUsedAdmin(ImportExportModelAdmin):
    list_display = [
        "id",
        "user",
        "gift_code",
        "used_at",
    ]
    list_display_links = ["id", "gift_code"]
    empty_value_display = "---"
    date_hierarchy = "used_at"


# @admin.register(Discount)
# class DiscountAdmin(ImportExportModelAdmin):
#     list_display = ["id", "title", "created_at"]
#     list_display_links = ["id", "title"]
#
#     empty_value_display = "---"
#     date_hierarchy = "created_at"
#     search_fields = ["title"]
