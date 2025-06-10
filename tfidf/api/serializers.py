from django.db import transaction
from rest_framework import serializers

from analyzer.models import Collection, Document
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
            raise serializers.ValidationError({
                'detail': 'Длина пароля должна быть не меньше 8 символов'
            })
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            'id',
            'username',
        )


class UserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)


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

    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            'id',
            'document',
            'owner',
            'word_frequency',
            'time_processed'
        )


class DocumentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            'document',
        )


class DocumentListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id',
            'title'
        )

    def get_title(self, obj):
        return obj.document.name


class DocumentRetrieveSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id',
            'content'
        )

    def get_content(self, obj):
        try:
            with open(obj.document.path, encoding='utf8') as f:
                data = f.read()
            return data
        except Exception:
            return None


class WordStatSerializer(serializers.Serializer):
    tf = serializers.FloatField()
    idf = serializers.FloatField()


class CollectionStatsSerializer(serializers.Serializer):
    collection_stats = serializers.DictField(
        child=serializers.DictField(child=WordStatSerializer())
    )


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = (
            'id',
            'documents',
        )


class CollectionRetrieveSerializer(serializers.ModelSerializer):
    documents = DocumentListSerializer(many=True)

    class Meta:
        model = Collection
        fields = (
            'id',
            'documents'
        )


class HuffmanEncodeSerializer(serializers.Serializer):
    code = serializers.DictField()
    encoded_text = serializers.CharField()
