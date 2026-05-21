from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import IndexApiView, LoginViewSet

router = DefaultRouter()
router.register(r"auth", LoginViewSet, basename="authentication")

urlpatterns = [
    path("", IndexApiView.as_view(), name="index"),
    path("", include(router.urls)),
]
