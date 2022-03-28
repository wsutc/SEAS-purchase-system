from django.urls import path
from purchases import views

urlpatterns = [
    path("", views.home, name="home"),
]