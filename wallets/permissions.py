from rest_framework import viewsets, permissions
from .models import Transaction
"""
Custom permissions to only allow merchants/clients to access certain actions.
"""

class IsMerchant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'merchant'

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'client'
    
class IsOwnerOrMerchant(permissions.BasePermission):
    """
    Only the wallet owner or merchants can view wallet details.
    """
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        # Merchants can view if they have a transaction with this wallet
        return request.user.user_type == 'merchant' and Transaction.objects.filter(wallet=obj, merchant=request.user).exists()

class CanRecharge(permissions.BasePermission):
    """
    Only clients can recharge their wallets.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user and request.user.user_type == 'client'

class CanCharge(permissions.BasePermission):
    """
    Allow merchants to charge wallets.
    """
    def has_object_permission(self, request, view, obj):
        # Check that the request.user is a merchant and the wallet is not owned by them
        return request.user.user_type == 'merchant' and obj.user != request.user
