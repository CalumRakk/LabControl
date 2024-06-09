from django.urls import path

from . import views

urlpatterns = [
    path("", views.aws, name="index"),
    path("api/browser-status", views.browser_status, name="browser_status"),
]
