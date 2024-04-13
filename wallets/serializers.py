from rest_framework import serializers
from .models import Wallet, Transaction

class WalletCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'token', 'balance']
        read_only_fields = ['token', 'balance']  # Token and balance are generated automatically

class WalletChargeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        """
        Checks that ampunt is not negative and that there is available balance.
        """
        wallet = self.context['wallet']
        if value <= 0:
            raise serializers.ValidationError("Charge amount must be greater than zero.")
        if wallet.balance < value:
            raise serializers.ValidationError("Insufficient funds available.")
        return value

    def create(self, validated_data):
        """
        Deduct the charge amount from the wallet's balance and create a transaction record.
        """
        wallet = self.context['wallet']
        wallet.balance -= validated_data['amount']
        wallet.save(update_fields=['balance'])
        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=validated_data['amount'],
            transaction_type='charge',
            status='success'
        )
        return transaction
    
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

class TransactionSerializer(serializers.ModelSerializer):
    """ Serializer for listing and displaying transaction details """
    class Meta:
        model = Transaction
        fields = ['id', 'wallet', 'amount', 'transaction_type', 'status', 'created_at']
        read_only_fields = ['wallet', 'amount', 'transaction_type', 'status', 'created_at'] # transactions are not modified after creation.

    def to_representation(self, instance):
        """ 
        Override to_representation to enhance the API response.
        Convert transaction type and status to display text
        """
        representation = super().to_representation(instance)
        representation['wallet'] = instance.wallet.token  # Displaying the wallet's token instead of the id
        representation['transaction_type'] = instance.get_transaction_type_display()
        representation['status'] = instance.get_status_display()
        return representation