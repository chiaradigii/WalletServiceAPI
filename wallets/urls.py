# wallets/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, TransactionViewSet, ClientWalletsListView

router = DefaultRouter()
router.register(r'wallets', WalletViewSet)
router.register(r'transactions', TransactionViewSet, basename='transaction')


urlpatterns = [
    path('', include(router.urls)),
    path('client-wallets/', ClientWalletsListView.as_view(), name='client-wallets-list'),
] + router.urls