import json
from time import perf_counter

import chardet
from django.conf import settings
from django.db.models import Avg, Count, Max, Min
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from analyzer.models import Collection, Document
from core.utils import (
    count_idfs, count_tf, delete_user_session, huffman_encode, huffman_decode,
    get_code
)
from users.models import User

from .permissions import IsOwnerOrStaff
from .serializers import (CollectionRetrieveSerializer, CollectionSerializer,
                          CollectionStatsSerializer, DocumentListSerializer,
                          DocumentPostSerializer, DocumentRetrieveSerializer,
                          DocumentSerializer, MetricSerializer,
                          PasswordSerializer, StatusSerializer,
                          UserPostSerializer, UserSerializer,
                          VersionSerializer, HuffmanEncodeSerializer)


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
                'type': 'object', 'properties': {'version': {'type': 'string'}}
            },
            401: {
                'type': 'object', 'properties': {'detail': {'type': 'string'}}
            }
        }
    )
    def get(self, request):
        message = 'V1.1.0'
        data = {
            'version': message
        }
        serializer = VersionSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MetricsView(APIView):
    @extend_schema(
        summary="Metrics",
        responses={
            200: OpenApiResponse(response=MetricSerializer,
                                 description='Metrics'),
        },
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
        return UserSerializer

    @extend_schema(
        summary='Add user',
        responses={
            201: {
                'type': 'object', 'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                }
            },
        },
    )
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_name='register',
        url_path='register'
    )
    def register(self, request):
        return self.create(request)

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

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsOwnerOrStaff(),]
        return super().get_permissions()

    @extend_schema(
        summary="Document list for current user",
        responses={
            200: OpenApiResponse(response=DocumentListSerializer,
                                 description='Document list for current user'),
        },
    )
    def list(self, request):
        queryset = Document.objects.filter(owner=request.user)
        serializer = DocumentListSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Document content",
        responses={
            200: OpenApiResponse(response=DocumentRetrieveSerializer,
                                 description='Document content'),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DocumentRetrieveSerializer(instance)
        return Response(serializer.data)

    @extend_schema(
        responses={
            201: {
                'type': 'object', 'properties': {
                    'document': {'type': 'string'}
                }
            },
        },
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'document': {'type': 'string', 'format': 'binary'}},
            },
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        raw_data = serializer.validated_data['document'].read()
        time_start = perf_counter()
        try:
            data = raw_data.decode('utf-8')
        except UnicodeDecodeError:
            encoding = chardet.detect(raw_data)['encoding']
            data = raw_data.decode(encoding)
        freq = count_tf(
            data,
            settings.ANALYZER_MIN_WORD_LENGTH,
            normalize=settings.ANALYZER_USE_NORMALIZE
        )
        time_end = perf_counter()
        serializer.save(
            owner=self.request.user,
            word_frequency=freq,
            time_processed=time_end - time_start
        )

    @extend_schema(
        summary="Document statistics by collection.",
        responses={
            200: OpenApiResponse(response=CollectionStatsSerializer,
                                 description='Document statistics'),
        },
    )
    @action(
        methods=['GET'],
        detail=True,
        url_path='statistics'
    )
    def get_statistic(self, request, *args, **kwargs):
        doc: Document = self.get_object()
        collections = doc.collection.all()
        result = {}
        word_stat = {}
        freqs = {
            k: v for k, v in sorted(
                doc.word_frequency.items(),
                key=lambda item: item[1]
                )[:settings.ANALYZER_WORDS_LIMIT]
        }
        for coll in collections:
            idfs = count_idfs(freqs, coll.documents.all())
            word_stat = {
                word: {
                    'tf': freqs[word],
                    'idf': idfs[word]
                } for word in freqs}
            result.update({coll.id: word_stat})
        serializer = CollectionStatsSerializer(data={
            'collection_stats': result
        })
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Encode document content by Huffman algorithm",
        responses={
            200: OpenApiResponse(response=HuffmanEncodeSerializer,
                                 description='Encoded document'),
        },
    )
    @action(
        methods=['GET'],
        detail=True,
        url_path='huffman'
    )
    def encode_text(self, request, *args, **kwargs):
        doc: Document = self.get_object()
        with open(doc.document.path, encoding='utf8') as f:
            text = f.read()

        encoded_text, codes = huffman_encode(text, doc.word_frequency)
        serializer = HuffmanEncodeSerializer(
            data={
                'code': codes,
                'encoded_text': encoded_text
            }
        )
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            200: {
                'type': 'object', 'properties': {
                    'text': {'type': 'string'}
                }
            },
        },
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'text': {'type': 'string', 'format': 'string'},
                    'code': {'type': 'string', 'format': 'string'}}
            },
        },
    )
    @action(
        methods=['POST'],
        detail=False,
        url_path='decode-text'
    )
    def decode_text(self, request):
        try:
            text: str = request.POST['text']
            code: dict = json.loads(request.POST['code'])
        except (KeyError, json.JSONDecodeError):
            return Response(
                {'detail': 'error'},
                status=status.HTTP_400_BAD_REQUEST
            )
        result = huffman_decode(text, code)
        data = {'text': result}
        return Response(data, status=status.HTTP_200_OK)


class CollectionViewSet(
    GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return CollectionRetrieveSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="Collection statistics",
        responses={
            200: OpenApiResponse(response=CollectionStatsSerializer,
                                 description='Collection statistics'),
        },
    )
    @action(
        methods=['GET'],
        detail=True,
        url_path='statistics'
    )
    def get_statistic(self, request, *args, **kwargs):
        coll = self.get_object()
        documents = coll.documents.all()
        result = {}
        freqs = {}
        text = ''
        for document in documents:
            text += ' '.join(document.word_frequency.keys()) + ' '
            freqs = count_tf(text, settings.ANALYZER_MIN_WORD_LENGTH)
        idfs = count_idfs(freqs, documents)
        result = {
            coll.id: {
                word: {'tf': freqs[word], 'idf': idfs[word]}
                for word in freqs.keys()
            }
        }
        serializer = CollectionStatsSerializer(data={
            'collection_stats': result
        })
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Add/delete document to collection",
        responses={
            201: OpenApiResponse(response=CollectionRetrieveSerializer,
                                 description='Added. Collection in response'),
            204: OpenApiResponse(response=None,
                                 description='Deleted.')
        },
    )
    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='document/(?P<document_id>[^/.]+)'
    )
    def add_delete_document(self, request, *args, **kwargs):
        collection = self.get_object()
        doc = get_object_or_404(Document, pk=kwargs.get('document_id'))
        if request.method == 'POST':
            collection.documents.add(doc)
        else:
            collection.documents.remove(doc)
        serializer = CollectionRetrieveSerializer(collection)
        if request.method == 'POST':
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
