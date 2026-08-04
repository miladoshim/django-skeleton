from rest_framework import serializers
from .models import GiftCode, IrBank, Payment, Payout, CoachIncome


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = ["price", "url"]


class PayoutSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payout
        fields = ["price", "url"]


class IrBankSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IrBank
        fields = ["price", "url"]


class GiftCodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GiftCode
        fields = ["price", "url"]


class CoachIncomeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CoachIncome
        fields = ["price", "url"]
