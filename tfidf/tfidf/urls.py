from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('auth/', include('users.urls')),
    path('', include('analyzer.urls', namespace='analyzer')),
]
