from django.urls import include, path
from rest_framework.routers import DefaultRouter

from account.views import AccountViewSet
from business.views import BusinessViewSet
from core.views import AuthViewSet, IndexApiView
from person.views import PersonViewSet
from transaction.views import TransactionViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="authentication")
router.register(r"transaction", TransactionViewSet, basename="transaction")
router.register(r"person", PersonViewSet, basename="person")
router.register(r"business", BusinessViewSet, basename="business")
router.register(r"account", AccountViewSet, basename="account")

urlpatterns = [
    path("", IndexApiView.as_view(), name="index"),
    path("", include(router.urls)),
]
