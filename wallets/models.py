from django.db import models
import uuid
from django.conf import settings

class Wallet(models.Model):
    # ForeignKey linking user model (many-to-one relationship)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallets')
    
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) # Unique token for wallet
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Track creation and updates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} - {self.balance} - {self.token}"
    

