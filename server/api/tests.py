from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Ping, User


class UserModelTests(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(
            email="test@example.com", password="StrongPass123!"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_success(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="AdminPass123!"
        )
        self.assertEqual(admin.email, "admin@example.com")
        self.assertTrue(admin.check_password("AdminPass123!"))
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_unique_constraint(self):
        User.objects.create_user(email="unique@example.com", password="StrongPass123!")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="unique@example.com", password="AnotherPass123!"
            )

    def test_password_strength_validation(self):
        # This should fail if password is too weak (e.g., '123')
        with self.assertRaises(ValidationError):
            User.objects.create_user(email="weakpass@example.com", password="123")

    def test_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="StrongPass123!")

    def test_password_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="nopass@example.com", password=None)


class PingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="pinguser@example.com", password="StrongPass123!"
        )

    def test_create_ping(self):
        ping = Ping.objects.create(user=self.user, latitude=10.0, longitude=20.0)
        self.assertEqual(ping.user, self.user)
        self.assertEqual(ping.latitude, 10.0)
        self.assertEqual(ping.longitude, 20.0)
        self.assertIsNotNone(ping.timestamp)

    def test_ping_trail(self):
        parent = Ping.objects.create(user=self.user, latitude=10.0, longitude=20.0)
        child = Ping.objects.create(
            user=self.user, latitude=11.0, longitude=21.0, parent_ping=parent
        )
        self.assertEqual(child.parent_ping, parent)

    def test_ping_requires_user(self):
        from django.db.utils import IntegrityError

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Ping.objects.create(user=None, latitude=10.0, longitude=20.0)

    def test_ping_requires_latitude_longitude(self):
        from django.db.utils import IntegrityError

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Ping.objects.create(user=self.user)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Ping.objects.create(user=self.user, latitude=10.0)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Ping.objects.create(user=self.user, longitude=20.0)

    def test_parent_ping_can_be_null(self):
        ping = Ping.objects.create(
            user=self.user, latitude=10.0, longitude=20.0, parent_ping=None
        )
        self.assertIsNone(ping.parent_ping)

    def test_str_representation(self):
        ping = Ping.objects.create(user=self.user, latitude=10.0, longitude=20.0)
        self.assertIn(self.user.email, str(ping))


class AuthTests(APITestCase):
    def setUp(self):
        self.user_email = "test@example.com"
        self.user_password = "$trongPass123!"
        self.user = User.objects.create_user(
            email=self.user_email, password=self.user_password
        )
        self.login_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.logout_url = reverse("token_blacklist")

    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            {"email": self.user_email, "password": self.user_password},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_login_failure(self):
        response = self.client.post(
            self.login_url,
            {"email": self.user_email, "password": "WrongPass123!"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access", response.data)

    def test_refresh_token(self):
        login_response = self.client.post(
            self.login_url, {"email": self.user_email, "password": self.user_password}
        )
        refresh_token = login_response.cookies.get("refresh_token").value
        self.client.cookies["refresh_token"] = refresh_token
        refresh_response = self.client.post(self.refresh_url)
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("refresh_token", refresh_response.cookies)

    def test_logout(self):
        login_response = self.client.post(
            self.login_url, {"email": self.user_email, "password": self.user_password}
        )
        refresh_token = login_response.cookies.get("refresh_token").value
        self.client.cookies["refresh_token"] = refresh_token
        logout_response = self.client.post(self.logout_url)
        self.assertEqual(logout_response.status_code, 200)
        self.assertNotIn("refresh_token", logout_response.cookies)


class RegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.valid_data = {
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "name": "New User",
            "code_name": "newbie",
        }

    def test_register_success(self):
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email=self.valid_data["email"]).exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(
            email=self.valid_data["email"], password=self.valid_data["password"]
        )
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("A user with that email already exists.", response.data["email"])

    def test_register_missing_fields(self):
        incomplete_data = self.valid_data.copy()
        incomplete_data["email"] = ""  # Missing email
        response = self.client.post(self.register_url, incomplete_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("This field may not be blank.", response.data["email"])

    def test_register_invalid_email(self):
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = "invalid-email"
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Enter a valid email address.", response.data["email"])

    def test_register_weak_password(self):
        weak_data = self.valid_data.copy()
        weak_data["password"] = "123"
        response = self.client.post(self.register_url, weak_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("This password is too short.", response.data["password"])
