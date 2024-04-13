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
class WalletViewSet(viewsets.ModelViewSet):
    """
    Viewset for `create`, `retrieve`, `update`, and `delete` actions for wallets.
    Custom actions that handle recharging and charging wallets.
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletStatusSerializer

    def get_serializer_class(self):
        # WalletCreateSerializer for create action - WalletStatusSerializer for list and retrieve actions
        if self.action in ['list', 'retrieve']:
            return WalletStatusSerializer
        return WalletCreateSerializer

    def get_queryset(self):
        # Ensures that users can only access their own wallets
        return Wallet.objects.filter(user=self.request.user)
  
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
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
    """
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        # Filter transactions to those related to user's wallets only
        return Transaction.objects.filter(wallet__user=user)
    
from django.shortcuts import render

def test_walletService(request):
    return render(request, 'wallets/test_walletService.html')