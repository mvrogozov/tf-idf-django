from time import perf_counter

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.conf import settings
from django.db.models import Min, Max, Avg, Count
from django.contrib.sessions.models import Session
from django.contrib.auth import logout as auth_logout
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import (
    ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
)
from rest_framework.mixins import (
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin,
)

from .serializers import (
    StatusSerializer, MetricSerializer, VersionSerializer,
    UserSerializer, UserPostSerializer, PasswordSerializer,
    DocumentSerializer, DocumentPostSerializer, DocumentListSerializer,
    DocumentRetrieveSerializer
)
from core.utils import delete_user_session, count_tf, count_idfs
from .permissions import IsOwnerOrStaff
from analyzer.models import Document, Collection
from users.models import User


class StatusView(APIView):
    @extend_schema(
        description="Status",
        request=None,
        responses={
            200: {
                'type': 'object', 'properties': {'status': {'type': 'string'}}
            },
            401: {
                'type': 'object', 'properties': {'detail': {'type': 'string'}}
            }
        }
    )
    def get(self, request):
        status_message = 'OK'
        data = {
            'status': status_message
        }
        serializer = StatusSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VersionView(APIView):
    @extend_schema(
        description="Version",
        request=None,
        responses={
            200: {
                'type': 'object', 'properties': {'status': {'type': 'string'}}
            },
            401: {
                'type': 'object', 'properties': {'detail': {'type': 'string'}}
            }
        }
    )
    def get(self, request):
        message = 'V1.0.1'
        data = {
            'version': message
        }
        serializer = VersionSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MetricsView(APIView):
    @extend_schema(
        description="Metrics",
        request=None,
        responses={
            200: {
                'type': 'string'
            },
            401: {
                'type': 'object', 'properties': {'detail': {'type': 'string'}}
            }
        }
    )
    def get(self, request):
        objs = Document.objects.all()
        if not objs:
            data = {
                'files_processed': 0,
                'min_time_processed': 0,
                'avg_time_processed': 0,
                'max_time_processed': 0,
                'max_file_size': 0,
                'min_file_size': 0,
                'avg_file_size': 0,
                'latest_file_processed': 0,
            }
        else:
            max_size = max(doc.document.size for doc in objs)
            min_size = min(doc.document.size for doc in objs)
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


class LogoutView(APIView):
    @extend_schema(
        description="Logout",
        request=None,
        responses={
            200: {
                'type': 'object', 'properties': {'status': {'type': 'string'}}
            },
            401: {
                'type': 'object', 'properties': {'detail': {'type': 'string'}}
            }
        }
    )
    def get(self, request):
        status_message = 'OK'
        data = {
            'status': status_message
        }
        response = Response(data=data, status=status.HTTP_200_OK)
        delete_user_session(request.user.pk)
        return response


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrStaff,)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'PUT']:
            return UserPostSerializer
        # if self.request.method == 'PATCH':
        #     return UserPasswordSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_name='register',
        url_path='register'
    )
    def register(self, request):
        return self.create(request)

    # def partial_update(self, request, *args, **kwargs):
    #     user = self.get_object()
    #     serializer = self.get_serializer(user, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     user.set_password(serializer.validated_data.get('password'))
    #     user.save()
    #     #self.perform_update(serializer)
    #     return Response(user.username)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = UserSerializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Change password for current user',
        responses={
            200: {
                'type': 'object', 'properties': {'detail': {'type': 'string'}}
            },
            400: {
                'type': 'object', 'properties': {'detail': {'type': 'string'}}
            },
            401: {
                'type': 'object', 'properties': {'detail': {'type': 'string'}}
            }
        },
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "current_password": {"type": "string"},
                    "new_password": {"type": "string"},
                },
            },
        }
    )
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = PasswordSerializer(data=request.data)
        serializer.validate(request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.check_password(
            serializer.validated_data.get('current_password')
        ):
            request.user.set_password(
                serializer.validated_data.get('new_password')
            )
            request.user.save()
            return Response(
                data={'detail': 'changed'}, status=status.HTTP_200_OK
            )
        return Response(
            data={'detail': 'wrong password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    def perform_destroy(self, instance):
        delete_user_session(instance.pk)
        return super().perform_destroy(instance)


class DocumentViewSet(
    GenericViewSet,
    RetrieveModelMixin,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin
):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated,]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentPostSerializer
        return super().get_serializer_class()

    def list(self, request):
        queryset = Document.objects.filter(owner=request.user)
        serializer = DocumentListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DocumentRetrieveSerializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        raw_data = serializer.validated_data['document'].read()
        time_start = perf_counter()
        freq = count_tf(raw_data, settings.ANALYZER_MIN_WORD_LENGTH)
        time_end = perf_counter()
        serializer.save(
            owner=self.request.user,
            word_frequency=freq,
            time_processed=time_end - time_start
        )

    @action(
        methods=['GET'],
        detail=True,
        url_path='statistics'
    )
    def get_statistic(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        a = Document.objects.get(id=pk)
        
        a = self.get_object()
        b = a.collection.all()
        return Response(f'stata - {b}', status=status.HTTP_200_OK)
