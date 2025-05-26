from rest_framework import serializers


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
