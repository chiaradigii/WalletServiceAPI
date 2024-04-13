from rest_framework import serializers
from .models import Wallet, Transaction

class WalletCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'token', 'balance']
        read_only_fields = ['token', 'balance']  # Token and balance are generated automatically


class WalletRechargeSerializer(serializers.Serializer):
    """ Serializer for recharging a wallet"""
    token = serializers.UUIDField(required=True) # Wallet token
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_token(self, value):
        if not Wallet.objects.filter(token=value).exists():
            raise serializers.ValidationError("Wallet with this token does not exist.")
        return value
    
    def create(self, validated_data):
        wallet = Wallet.objects.get(token=validated_data['token'])
        wallet.balance += validated_data['amount']
        wallet.save()
        # Create a transaction record
        transaction = Transaction.objects.create(wallet=wallet, amount=validated_data['amount'], transaction_type='recharge')
        return transaction

class WalletStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['token', 'balance', 'created_at', 'updated_at']