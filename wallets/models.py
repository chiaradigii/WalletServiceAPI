from django.db import models
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError


class Wallet(models.Model):
    # ForeignKey linking user model 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallets')
    
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # Unique token for wallet
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        # Check if merchant and ensure they don't have more than one wallet
        if self.user.user_type == 'merchant':
            existing_wallets = Wallet.objects.filter(user=self.user)
            if existing_wallets.exists() and (not self.pk or self.pk not in existing_wallets.values_list('id', flat=True)):
                raise ValidationError('Merchants can only have one wallet')


    # Save method to validate wallet
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.balance} - {self.token}"
    

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('charge', 'Charge'),
        ('recharge', 'Recharge'),
    )
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    # A wallet can have multiple transactions
    wallet = models.ForeignKey('Wallet', related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=8, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='success')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            transaction_by = 'Merchant' if self.wallet.user.user_type == 'merchant' else 'Client'
            return f"{transaction_by} Transaction: {self.transaction_type} - {self.status} - {self.amount}"