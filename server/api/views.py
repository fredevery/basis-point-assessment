from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from .models import Ping
from .permissions import IsOwnerOrReadOnly
from .serializers import PingSerializer, RegisterSerializer

LATEST_PINGS_COUNT = 3


def set_refresh_token_cookie(response, refresh_token):
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=60 * 60 * 24 * 7,  # 1 week
        )
        del response.data["refresh"]
    return response


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response = set_refresh_token_cookie(
                response, response.data.get("refresh", None)
            )
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            request.data["refresh"] = refresh_token
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200 and "refresh" in response.data:
            response = set_refresh_token_cookie(
                response, response.data.get("refresh", None)
            )
        return response


class CustomTokenBlacklistView(TokenBlacklistView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            request.data["refresh"] = refresh_token
        response = super().post(request, *args, **kwargs)
        if response.status_code == 204:
            response.delete_cookie("refresh_token")
        return response


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PingViewSet(viewsets.ModelViewSet):
    queryset = Ping.objects.all()
    serializer_class = PingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["user", "timestamp"]
    ordering_fields = ["timestamp", "latitude", "longitude"]
    ordering = ["-timestamp"]

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def latest(self, request):
        latest_pings = self.queryset.order_by("-timestamp")[:LATEST_PINGS_COUNT]
        serializer = self.get_serializer(latest_pings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="respond",
        permission_classes=[permissions.IsAuthenticated],
    )
    def respond(self, request, pk=None):
        parent_ping = self.get_object()
        user = request.user
        data = request.data.copy()
        data.update(
            {
                "user": user.id,
                "parent_ping": parent_ping.id,
            }
        )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        header = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=header)
