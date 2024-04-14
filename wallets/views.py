from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
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

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return WalletStatusSerializer
        return WalletCreateSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            wallets = Wallet.objects.filter(user=self.request.user)
            print(f"Wallets found: {wallets.count()}")
            print(f"Wallets: {wallets}")
            return wallets
        print("No authenticated user, returning none")
        return Wallet.objects.none()
    
    def get_object(self):
        try:
            obj = super().get_object()
            print(f"Object found: {obj}")
            return obj
        except Http404:
            print("Object not found leading to 404.")
            raise
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise

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
    def charge(self, request, pk=None):
        """Charge a client's wallet."""
        print("Charge method called")
        print(f"Request by user: {request.user}, is merchant: {request.user.is_merchant}")

        try:
            wallet = self.get_object()
            print(f"Wallet found: {wallet.id}")
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
