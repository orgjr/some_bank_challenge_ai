from django.urls import include, path
from rest_framework.routers import DefaultRouter

from account.views import AccountViewSet
from business.views import BusinessViewSet
from core.views import AuthViewSet, HealthCheckAPIView, IndexAPIView
from person.views import PersonViewSet
from transaction.views import TransferViewSet
from user.views import GetUserAPIView

router = DefaultRouter()
router.register(r"transfers", TransferViewSet, basename="transfer")
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"persons", PersonViewSet, basename="person")
router.register(r"business", BusinessViewSet, basename="business")

auth_router = DefaultRouter()
auth_router.register("", AuthViewSet, basename="authentication")

urlpatterns = [
    path("", IndexAPIView.as_view(), name="index"),
    path("health/", HealthCheckAPIView.as_view(), name="health"),
    path("users/me/", GetUserAPIView.as_view(), name="user-detail"),
    path("", include(router.urls)),
    path("", include(auth_router.urls)),
]
