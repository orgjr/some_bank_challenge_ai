from django.urls import include, path
from rest_framework.routers import DefaultRouter

from account.views import AccountViewSet
from core.views import IndexApiView, LoginViewSet
from store.views import StoreViewSet
from transaction.views import TransactionViewSet
from user.views import UserViewSet

router = DefaultRouter()
router.register(r"auth", LoginViewSet, basename="authentication")
router.register(r"transaction", TransactionViewSet, basename="transaction")
router.register(r"user", UserViewSet, basename="user")
router.register(r"store", StoreViewSet, basename="store")
router.register(r"account", AccountViewSet, basename="account")

urlpatterns = [
    path("", IndexApiView.as_view(), name="index"),
    path("", include(router.urls)),
]
