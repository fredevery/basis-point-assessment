from django.contrib.auth import password_validation as validators
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Ping, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "name", "code_name", "password")
        extra_kwargs = {
            "name": {"required": False, "allow_blank": True},
            "code_name": {"required": False, "allow_blank": True},
        }

    def validate_password(self, value):
        try:
            User.objects.model().set_password(value)
            validators.validate_password(password=value, user=User())
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
            code_name=validated_data.get("code_name", ""),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name", "code_name")
        read_only_fields = ("id",)


class PingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ping
        fields = "__all__"
