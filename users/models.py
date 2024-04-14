"""
This model will serve as the foundation for handling both client and commerce users.
Different types of users are considered, with endpoints for performing the following operations:

Client: must be able to register for the service, create one or more wallet accounts (which will be identified by a unique token), recharge the balance of their accounts, check the status of their accounts, and list the transactions of their accounts.
Merchant: must be able to register for the service, create a wallet account, charge a client's wallet account using the account's token as a reference, and list the transactions of their merchant account.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """ Create a superuser with email and password """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        ('client', 'Client'),
        ('merchant', 'Merchant'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='client')
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

