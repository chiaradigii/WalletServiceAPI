from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, Transaction
from rest_framework import viewsets
from .serializers import WalletCreateSerializer, WalletStatusSerializer, TransactionSerializer
from rest_framework.decorators import action
from rest_framework import status
from .serializers import WalletRechargeSerializer, WalletChargeSerializer
from .permissions import IsClient, IsMerchant, IsOwnerOrMerchant

class WalletViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return a wallet instance.

    list:
    Return all wallets, filtered by the current user.

    create:
    Create a new wallet instance.

    recharge:
    Recharge a wallet balance.

    charge:
    Charge a client's wallet.
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletStatusSerializer

    def get_serializer_class(self):
        # WalletCreateSerializer for create action - WalletStatusSerializer for list and retrieve actions
        if self.action in ['list', 'retrieve']:
            return WalletStatusSerializer
        return WalletCreateSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Wallet.objects.filter(user=self.request.user)
        else:
            return Wallet.objects.none()
  
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsClient])
    def recharge(self, request, pk=None):
        """ Recharge a wallet and create a transaction record."""
        wallet = self.get_object()
        serializer = WalletRechargeSerializer(data=request.data, context={'wallet': wallet})
        if serializer.is_valid():
            try:
                # Ensure that both operations are done atomically
                with transaction.atomic():
                    serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsMerchant])
    def charge(self, request, pk=None):
        """
        Widraw an amount from a wallet and create a transaction record.
        This must be done atomically to prevent inconsistencies
        """
        wallet = self.get_object()
        serializer = WalletChargeSerializer(data=request.data, context={'wallet': wallet})
        if serializer.is_valid():
            try:
                with transaction.atomic(): # Ensures that both operations are done atomically
                    serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            wallet = Wallet.objects.get(user=request.user)
            serializer = WalletStatusSerializer(wallet)
            return Response(serializer.data)
        except Wallet.DoesNotExist:
            return Response({"message": "Wallet not found"}, status=404)

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset that provides `list` and `retrieve` actions for transactions.
    Filter transactions by user_type.
    """
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'merchant':
            return Transaction.objects.filter(merchant=user) # Merchants can see transactions here they have charged
        elif user.user_type == 'client':
            return Transaction.objects.filter(wallet__user=user) # Clients can see their transactions
        else:
            return Transaction.objects.none()
           
from django.shortcuts import render

def test_walletService(request):
    return render(request, 'wallets/test_walletService.html')