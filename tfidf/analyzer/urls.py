from django.urls import path

from . import views

app_name = 'analyzer'

urlpatterns = [
    path('', views.DocumentCreateView.as_view(), name='index'),
    path(
        'report/<int:document_id>',
        views.ReportView.as_view(),
        name='report'
    ),
]
