from django.urls import include, path

urlpatterns = [
    path("bank/", include("core.urls")),
]
