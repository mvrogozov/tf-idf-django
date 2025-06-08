from djoser.serializers import \
    UserCreateSerializer as BaseUserRegistrationSerializer
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


# class UserRegistrationSerializer(BaseUserRegistrationSerializer):
#     class Meta(BaseUserRegistrationSerializer.Meta):
#         fields = ('id', 'email', 'first_name', 'last_name', 'username')


# class CustomUserCreateSerializer(UserCreateSerializer):
#     password = serializers.CharField(style={"input_type": "password"}, write_only=True)

#     class Meta(UserCreateSerializer.Meta):
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name'
        )
