from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Ping, User

VALID_USER_DATA = {
    "email": "test@example.com",
    "password": "$trongPass123!",
    "name": "Test User",
    "code_name": "testuser",
}

VALID_USER_DATA_2 = {
    "email": "test2@example.com",
    "password": "AnotherStrongPass123!",
    "name": "Test User 2",
    "code_name": "testuser2",
}


class UserModelTests(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(
            email=VALID_USER_DATA["email"], password=VALID_USER_DATA["password"]
        )
        self.assertEqual(user.email, VALID_USER_DATA["email"])
        self.assertTrue(user.check_password(VALID_USER_DATA["password"]))
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
            email=VALID_USER_DATA["email"], password=VALID_USER_DATA["password"]
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
        self.valid_data = VALID_USER_DATA.copy()

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
        self.assertIn(
            "This password is too short.", " ".join(response.data["password"])
        )


class PingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**VALID_USER_DATA)
        self.other_user = User.objects.create_user(**VALID_USER_DATA_2)
        self.ping = Ping.objects.create(user=self.user, latitude=10.0, longitude=20.0)
        self.ping_list_url = reverse("ping-list")
        self.ping_detail_url = reverse("ping-detail", kwargs={"pk": self.ping.pk})
        self.ping_latest_url = reverse("ping-latest")

    def test_authenticated_user_can_create_ping(self):
        self.client.force_authenticate(user=self.user)
        data = {"latitude": 12.34, "longitude": 56.78, "user": self.user.id}
        response = self.client.post(self.ping_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ping.objects.count(), 2)

    def test_unauthenticated_user_cannot_create_ping(self):
        data = {"latitude": 12.34, "longitude": 56.78}
        response = self.client.post(self.ping_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_retrieve_ping(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.ping_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.ping.id)

    def test_authenticated_user_can_update_own_ping(self):
        self.client.force_authenticate(user=self.user)
        data = {"latitude": 99.99, "longitude": 88.88}
        response = self.client.patch(self.ping_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ping.refresh_from_db()
        self.assertEqual(self.ping.latitude, 99.99)

    def test_authenticated_user_cannot_update_others_ping(self):
        self.client.force_authenticate(user=self.other_user)
        data = {"latitude": 77.77}
        response = self.client.patch(self.ping_detail_url, data)
        # Adjust expected status if you implement custom permissions
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_authenticated_user_can_delete_own_ping(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.ping_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ping.objects.filter(id=self.ping.id).exists())

    def test_authenticated_user_cannot_delete_others_ping(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.ping_detail_url)
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_unauthenticated_user_cannot_access_ping_endpoints(self):
        response = self.client.get(self.ping_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(self.ping_list_url, {"latitude": 1, "longitude": 2})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(self.ping_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_latest_endpoint_returns_last_three_pings(self):
        self.client.force_authenticate(user=self.user)
        for i in range(3):
            Ping.objects.create(user=self.user, latitude=10.0 + i, longitude=20.0 + i)
        response = self.client.get(self.ping_latest_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["latitude"], 12.0)
        self.assertEqual(response.data[1]["latitude"], 11.0)
        self.assertEqual(response.data[2]["latitude"], 10.0)

    def test_authenticated_user_can_respond_to_ping(self):
        self.client.force_authenticate(user=self.user)
        # Create a ping to respond to
        parent_ping = Ping.objects.create(
            user=self.other_user, latitude=50.0, longitude=60.0
        )
        url = reverse("ping-respond", kwargs={"pk": parent_ping.id})
        data = {"latitude": 51.4, "longitude": 61.6}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["parent_ping"], parent_ping.id)
        self.assertEqual(response.data["user"], self.user.id)

    def test_unauthenticated_user_cannot_respond_to_ping(self):
        parent_ping = Ping.objects.create(user=self.user, latitude=50.0, longitude=60.0)
        url = reverse("ping-respond", args=[parent_ping.id])
        data = {"latitude": 51.0, "longitude": 61.0}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ping_list_filter_by_user(self):
        self.client.force_authenticate(user=self.user)
        # Create pings for another user
        for _ in range(3):
            Ping.objects.create(user=self.other_user, latitude=1, longitude=1)
        response = self.client.get(self.ping_list_url, {"user": self.user.id})
        self.assertEqual(response.status_code, 200)
        for ping in response.data["results"]:
            self.assertEqual(ping["user"], self.user.id)
