from django.urls import path

from core.views import IndexApiView

urlpatterns = [
    path("bank", IndexApiView.as_view(), name="index"),
]
