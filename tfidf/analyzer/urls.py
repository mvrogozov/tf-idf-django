from django.urls import path

from . import views

app_name = 'analyzer'

urlpatterns = [
    path('', views.DocumentCreateView.as_view(), name='index'),
]
