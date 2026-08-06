from rest_framework import serializers
from .models import Payment, Wallet, WalletTransaction


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = ["price", "url"]


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Wallet
        fields = ["user", "balance"]


class WalletTransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ["user", "tracking_code", "amount", "is_processed", "processed_at"]
