import logging
from django.shortcuts import render
from django.urls import reverse
from django.db import transaction
from azbankgateways import (
    bankfactories,
)
from azbankgateways.exceptions import AZBankGatewaysException
from apps.financial.models import Payment as PaymentModel


class Payment:
    request = None
    amount = None
    payment_for = None
    object_id_for = None
    callback_url = None

    def __init__(
        self, request, amount, callback_url, payment_for=None, object_id_for=None
    ):
        self.request = request
        self.amount = amount
        self.payment_for = payment_for
        self.object_id_for = object_id_for
        self.callback_url = callback_url

    @transaction.atomic
    def go_to_gateway(self):
        user = self.request.user
        amount = self.amount
        user_mobile_number = user.mobile

        factory = bankfactories.BankFactory()
        try:
            bank = factory.auto_create()
            bank.set_request(self.request)
            bank.set_amount(amount)
            bank.set_client_callback_url(reverse(self.callback_url))
            bank.set_mobile_number(user_mobile_number)

            bank_record = bank.ready()
            PaymentModel.objects.create(
                user=user,
                result=bank_record,
                final_amount=amount,
                payment_for=self.payment_for,
                object_id_for=self.object_id_for,
                tracking_code=bank_record.tracking_code,
            )

            context = bank.get_gateway()
            return render(
                self.request,
                "financial/redirect_to_bank.html",
                context=context,
            )
        except AZBankGatewaysException as e:
            logging.critical(e)
            return render(self.request, "financial/redirect_to_bank.html")
