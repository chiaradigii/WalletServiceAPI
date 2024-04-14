from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wallets/',include('wallets.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('users/', include('users.urls')),
]
