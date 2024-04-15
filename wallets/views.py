from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, Transaction
from rest_framework import viewsets
from .serializers import WalletCreateSerializer, WalletStatusSerializer, TransactionSerializer
from rest_framework.decorators import action
from rest_framework import status
from .serializers import WalletRechargeSerializer, WalletChargeSerializer
from .permissions import IsClient, IsMerchant

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
    lookup_field = 'token'

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return WalletStatusSerializer
        return WalletCreateSerializer

    def get_queryset(self):
        if self.request.user.user_type == 'merchant':
            return Wallet.objects.all()
        return Wallet.objects.filter(user=self.request.user)
    
    def get_object(self):
        """ Retrieves the object using the UUID token"""
        # Use the lookup_field and the value from the URL kwargs to filter the queryset
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        obj = get_object_or_404(self.get_queryset(), **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj


    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsClient])
    def recharge(self, request, pk=None):
        wallet = self.get_object()
        serializer = WalletRechargeSerializer(data=request.data, context={'wallet': wallet})
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsMerchant])
    def charge(self, request, token=None):
        """Charge a client's wallet."""
        if request.user.user_type != 'merchant':
            return Response({"message": "Unauthorized - Only merchants can perform this action"}, status=status.HTTP_403_FORBIDDEN)
    
        try:
            wallet = get_object_or_404(Wallet, token=token)
            print(f"Wallet found: {wallet.token}")
        except Wallet.DoesNotExist:
            print("Wallet not found")
            return Response({"message": "Wallet not found"}, status=404)
        
        serializer = WalletChargeSerializer(data=request.data, context={'wallet': wallet})
        if serializer.is_valid():
            try:
                with transaction.atomic():
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
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'merchant':
            # Assuming merchants can see all transactions they are involved in
            return Transaction.objects.filter(wallet__user=user)
        return Transaction.objects.filter(wallet__user=user)  # Clients can see their transactions

class ClientWalletsListView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request, *args, **kwargs):
        wallets = Wallet.objects.filter(user__user_type='client')
        serializer = WalletStatusSerializer(wallets, many=True)
        return Response(serializer.data)
