# def wallet_gift_charge(request):
#         user = request.user
#         code = request.POST.get("code")

#         gift = GiftCode.objects.filter(code=code).first()
#         if not gift:
#             messages.error(request, "کد هدیه موجود نمی باشد")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

#         if not gift.user_can_use(user):
#             messages.error(request, "شما قبلا از این کد هدیه استفاده کرده اید.")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

#         if not gift.can_use:
#             messages.error(request, "کد هدیه قابل استفاده نمی باشد")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

#         if gift.apply(user):
#             messages.success(request, "کیف پول شما شارژ شد.")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))
#         else:
#             messages.error(request, "خطا در اعمال کد هدیه.")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))


# def wallet_charge(request):
#     if request.method == "POST":
#         user = request.user
#         amount = int(request.POST.get("amount"))
#         if amount < 100000:
#             messages.error(request, "مبلغ کم تر از صد هزار تومان می باشد.")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

#         callback_url = "apps.accounts:dashboard_financial_wallet_charge_callback"
#         pay = PaymentService(
#             request=request,
#             amount=amount,
#             payment_for="a",
#             callback_url=callback_url,
#         )
#         return pay.go_to_gateway()


# def wallet_charge_callback(request):
#     tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
#     if not tracking_code:
#         logging.debug("این لینک معتبر نیست.")
#         raise Http404

#     try:
#         bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
#     except bank_models.Bank.DoesNotExist:
#         logging.debug("این لینک معتبر نیست.")
#         raise Http404

#     if bank_record.is_success:
#         user = request.user

#         user.wallet.charge(bank_record.amount)

#         context = {
#             "success": True,
#             "message": "کیف شما به مبلغ شارژ شد",
#             "tc": tracking_code,
#             "btn_url": "apps.accounts:dashboard_financial",
#             "btn_title": "رفتن به کیف پول",
#         }
#         return render(request, "financial/payment_result.html", context=context)

#     context = {
#         "success": False,
#         "message": "پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.",
#         "tc": tracking_code,
#         "btn_url": "apps.accounts:dashboard_financial",
#         "btn_title": "رفتن به کیف پول",
#     }
#     return render(request, "financial/payment_result.html", context=context)
