from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name'
        )
