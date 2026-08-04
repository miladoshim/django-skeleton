import logging
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from azbankgateways import (
    bankfactories,
)
from azbankgateways import (
    default_settings as settings,
)
from azbankgateways import (
    models as bank_models,
)
from azbankgateways.exceptions import AZBankGatewaysException
from .models import Payment


# @login_required("apps.accounts:login_view")
def go_to_gateway_view(request):
    user = request.user
    amount = 20000
    user_mobile_number = user.mobile

    factory = bankfactories.BankFactory()
    try:
        bank = factory.auto_create()
        bank.set_request(request)
        bank.set_amount(amount)
        bank.set_client_callback_url(reverse("apps.financial:callback_gateway"))
        bank.set_mobile_number(user_mobile_number)

        # در صورت تمایل اتصال این رکورد به رکورد فاکتور یا هر چیزی که بعدا بتوانید ارتباط بین محصول یا خدمات را با این
        # پرداخت برقرار کنید.
        bank_record = bank.ready()

        Payment.objects.create(result=bank_record, user=user)

        # هدایت کاربر به درگاه بانک
        context = bank.get_gateway()
        return render(request, "financial/redirect_to_bank.html", context=context)
    except AZBankGatewaysException as e:
        logging.critical(e)
        return render(request, "financial/redirect_to_bank.html")


def callback_gateway_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    # در این قسمت باید از طریق داده هایی که در بانک رکورد وجود دارد، رکورد متناظر یا هر اقدام مقتضی دیگر را انجام دهیم
    if bank_record.is_success:
        # پرداخت با موفقیت انجام پذیرفته است و بانک تایید کرده است.
        # می توانید کاربر را به صفحه نتیجه هدایت کنید یا نتیجه را نمایش دهید.

        # wallet charge, create order
        context = {
            "success": True,
            "message": "پرداخت با موفقیت انجام شد.",
            "tc": tracking_code,
        }
        return render(request, "financial/payment_result.html", context=context)

    context = {
        "success": False,
        "message": "پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.",
        "tc": tracking_code,
    }
    return render(request, "financial/payment_result.html", context=context)


# class PaymentVerifyView(LoginRequiredMixin, View):
#     @method_decorator(csrf_protect)
#     def post(self, request, *args, **kwargs):
#         try:
#             payment_id = request.POST.get('payment_id')
#             payment = Payment.objects.get(payment_id=payment_id)
#             return JsonResponse({'status': 'success', 'order_id': payment.order.uid, 'payment_status': payment.status})
#         except Payment.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
