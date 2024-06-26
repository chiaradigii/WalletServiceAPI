from django.contrib.auth import get_user_model
from rest_framework import serializers
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """ Serializer for user registration"""
    class Meta:
        model = User
        fields = ['email', 'password', 'user_type'] 
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            user_type=validated_data['user_type']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user