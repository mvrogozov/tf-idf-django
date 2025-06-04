from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Min, Max, Avg, Count
from django.contrib.sessions.models import Session
from django.contrib.auth import logout as auth_logout
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


from .serializers import (
    StatusSerializer, MetricSerializer, VersionSerializer,
    UserSerializer, UserPostSerializer, PasswordSerializer,
    UserPasswordSerializer
)
from .utils import delete_user_session
from .permissions import IsOwnerOrStaff
from analyzer.models import Document
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
            return Response(status=status.HTTP_200_OK)
        return Response('wrong password', status=status.HTTP_401_UNAUTHORIZED)

    def perform_destroy(self, instance):
        delete_user_session(instance.pk)
        return super().perform_destroy(instance)
