from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Min, Max, Avg, Count
from django.db.models.functions import Length

from .serializers import StatusSerializer, MetricSerializer, VersionSerializer
from analyzer.models import Document


class StatusView(APIView):
    def get(self, request):
        status_message = 'OK'
        data = {
            'status': status_message
        }
        serializer = StatusSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VersionView(APIView):
    def get(self, request):
        message = 'V1'
        data = {
            'version': message
        }
        serializer = VersionSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MetricsView(APIView):
    def get(self, request):
        objs = Document.objects.all()
        max_size = max(doc.document.size for doc in objs) if objs else 0
        min_size = min(doc.document.size for doc in objs) if objs else 0
        avg_size = (
            sum(doc.document.size for doc in objs) // objs.count()
            if objs else 0
        )
        stats = Document.objects.aggregate(
            min_time=Min('time_processed'),
            avg_time=Avg('time_processed'),
            max_time=Max('time_processed'),
            total_files=Count('id')
        )
        data = {
            'files_processed': stats['total_files'],
            'min_time_processed': f'{stats["min_time"]:.3f}',
            'avg_time_processed': f'{stats["avg_time"]:.3f}',
            'max_time_processed': f'{stats["max_time"]:.3f}',
            'max_file_size': max_size,
            'min_file_size': min_size,
            'avg_file_size': avg_size,
            'latest_file_processed': f'{objs.last().time_processed:.3f}',
        }
        serializer = MetricSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
