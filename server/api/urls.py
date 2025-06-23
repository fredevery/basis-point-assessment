from django.urls import path
from rest_framework import routers

from .views import (
    CustomTokenBlacklistView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    PingViewSet,
    RegisterView,
)

router = routers.SimpleRouter()
router.register(r"pings", PingViewSet, basename="ping")

urlpatterns = [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", CustomTokenBlacklistView.as_view(), name="token_blacklist"),
    path("auth/register/", RegisterView.as_view(), name="register"),
] + router.urls
