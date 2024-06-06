from django.urls import path

from . import views

urlpatterns = [
    path("", views.auto, name="index"),
]
