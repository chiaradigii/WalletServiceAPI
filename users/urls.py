from django.urls import path
from .views import ClientRegistrationView, MerchantRegistrationView

urlpatterns = [
    path('register/client/', ClientRegistrationView.as_view(), name='client-registration'),
    path('register/merchant/', MerchantRegistrationView.as_view(), name='merchant-registration'),
]