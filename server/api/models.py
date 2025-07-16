from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            validate_password(password, user=user)
            user.set_password(password)
        else:
            raise ValueError("The Password field must be set")
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True, error_messages={"unique": "A user with that email already exists."}
    )
    name = models.CharField(
        max_length=30,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z ]*$",
                message="Name must be alphanumeric or contain underscores, dots, or hyphens.",
                code="invalid_name",
            )
        ],
    )
    code_name = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9]*$",
                message="Code name must be alphanumeric or contain underscores, dots, or hyphens.",
                code="invalid_code_name",
            )
        ],
        error_messages={"unique": "A user with that code name already exists."},
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "code_name"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Ping(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pings"
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent_ping = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="child_pings",
    )

    def __str__(self):
        return f"Ping by {self.user.email} at {self.timestamp} ({self.latitude}, {self.longitude})"

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["parent_ping"]),
        ]
