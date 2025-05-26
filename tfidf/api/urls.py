from django.urls import include, path

from api.views import StatusView, MetricsView, VersionView

app_name = 'api'
API_VERSION = 'v1/'

urlpatterns = [
    path(API_VERSION + 'status/', StatusView.as_view(), name='status'),
    path(API_VERSION + 'version/', VersionView.as_view(), name='version'),
    path(API_VERSION + 'metrics/', MetricsView.as_view(), name='metrics')
]
