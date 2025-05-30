from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
)

from api.views import StatusView, MetricsView, VersionView

app_name = 'api'
API_VERSION = 'v1/'

urlpatterns = [
    path(API_VERSION + 'status/', StatusView.as_view(), name='status'),
    path(API_VERSION + 'version/', VersionView.as_view(), name='version'),
    path(API_VERSION + 'metrics/', MetricsView.as_view(), name='metrics'),
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
]
