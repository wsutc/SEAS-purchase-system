from django.urls import path
from purchases import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add-mfg/", views.add_manufacturer, name="add_manufacturer")
]
