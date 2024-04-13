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
        # Check if client is a merchant and already has a wallet
        if self.user.user_type == 'merchant' and Wallet.objects.filter(user=self.user).exists():
            raise ValidationError('Merchant already has a wallet')

    # Save method to validate wallet
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} - {self.balance} - {self.token}"
    

