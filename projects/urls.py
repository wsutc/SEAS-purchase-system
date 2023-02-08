# flake8: noqa
from django.urls import path

from .views import ProjectCreateView, ProjectDetailView, ProjectListView

urlpatterns = [
    path("", ProjectListView.as_view(), name="list_project"),
    path("create/", ProjectCreateView.as_view(), name="create_project"),
    path("<str:slug>/", ProjectDetailView.as_view(), name="detail_project"),
]
