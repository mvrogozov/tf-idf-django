from rest_framework import serializers
from django.db import transaction

from users.models import User


class StatusSerializer(serializers.Serializer):
    status = serializers.CharField()


class VersionSerializer(serializers.Serializer):
    version = serializers.CharField()


class MetricSerializer(serializers.Serializer):
    files_processed = serializers.IntegerField()
    min_time_processed = serializers.FloatField()
    avg_time_processed = serializers.FloatField()
    max_time_processed = serializers.FloatField()
    latest_file_processed = serializers.FloatField()
    max_file_size = serializers.IntegerField()
    min_file_size = serializers.IntegerField()
    avg_file_size = serializers.IntegerField()


class PasswordSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        return {
            'current_password': data['current_password'],
            'new_password': data['new_password']
        }

    def validate(self, data):
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        if not current_password:
            raise serializers.ValidationError({
                'current_password': 'Обязательное поле'
            })
        if not new_password:
            raise serializers.ValidationError({
                'new_password': 'Обязательное поле'
            })
        if len(new_password) < 8:
            raise serializers.ValidationError(
                'Длина пароля должна быть не меньше 8 символов'
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            'id',
            'username',
        )


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'password'
        )

    @transaction.atomic()
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
