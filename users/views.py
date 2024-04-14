from django.shortcuts import render

from rest_framework import generics
from .models import User
from .serializers import UserRegistrationSerializer

class ClientRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.none() # Required for DjangoModelPermissions

    def perform_create(self, serializer):
        serializer.save(user_type='client')

class MerchantRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.none() 

    def perform_create(self, serializer):
        serializer.save(user_type='merchant')
