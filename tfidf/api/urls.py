from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
)
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter

from djoser.views import UserViewSet as DjUserViewSet

from api.views import (
    StatusView, MetricsView, VersionView, LogoutView, UserViewSet,
    DocumentViewSet, CollectionViewSet
)

app_name = 'api'
API_VERSION = 'v1/'

router = DefaultRouter()

router.register('users', UserViewSet, basename='api_users')
router.register('documents', DocumentViewSet, basename='api_documents')
router.register('collections', CollectionViewSet, basename='api_collections')


urlpatterns = [
    path(API_VERSION + 'status/', StatusView.as_view(), name='status'),
    path(API_VERSION + 'version/', VersionView.as_view(), name='version'),
    path(API_VERSION + 'metrics/', MetricsView.as_view(), name='metrics'),
    path(API_VERSION, include(router.urls), name='api_list'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='api:schema'),
        name='swagger-ui'
    ),
    path(
        'schema/redoc/',
        SpectacularRedocView.as_view(url_name='api:schema'),
        name='redoc'
    ),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),
    path(
        'auth/login/',
        jwt_views.TokenObtainPairView.as_view(),
        name='jwt-create'
    ),
    path(
        'auth/jwt/refresh/',
        jwt_views.TokenRefreshView.as_view(),
        name='jwt-refresh'
    ),
    path(
        'auth/jwt/verify/',
        jwt_views.TokenVerifyView.as_view(),
        name='jwt-verify'
    ),
    # path(
    #     'users/register/',
    #     DjUserViewSet.as_view({'post': 'create'}),
    #     name='user-create'
    # ),
    # path(
    #     'users/<int:id>/',
    #     DjUserViewSet.as_view({'delete': 'destroy'}),
    #     name='user-delete'
    # ),
]
