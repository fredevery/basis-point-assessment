from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from .models import User, Ping

class UserModelTests(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(email='test@example.com', password='StrongPass123!')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('StrongPass123!'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_success(self):
        admin = User.objects.create_superuser(email='admin@example.com', password='AdminPass123!')
        self.assertEqual(admin.email, 'admin@example.com')
        self.assertTrue(admin.check_password('AdminPass123!'))
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_unique_constraint(self):
        User.objects.create_user(email='unique@example.com', password='StrongPass123!')
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='unique@example.com', password='AnotherPass123!')

    def test_password_strength_validation(self):
        # This should fail if password is too weak (e.g., '123')
        with self.assertRaises(ValidationError):
            User.objects.create_user(email='weakpass@example.com', password='123')

    def test_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='StrongPass123!')

    def test_password_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='nopass@example.com', password=None)

class PingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='pinguser@example.com', password='StrongPass123!')

    def test_create_ping(self):
        ping = Ping.objects.create(user=self.user, latitude=10.0, longitude=20.0)
        self.assertEqual(ping.user, self.user)
        self.assertEqual(ping.latitude, 10.0)
        self.assertEqual(ping.longitude, 20.0)
        self.assertIsNotNone(ping.timestamp)

    def test_ping_trail(self):
        parent = Ping.objects.create(user=self.user, latitude=10.0, longitude=20.0)
        child = Ping.objects.create(user=self.user, latitude=11.0, longitude=21.0, parent_ping=parent)
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
        ping = Ping.objects.create(user=self.user, latitude=10.0, longitude=20.0, parent_ping=None)
        self.assertIsNone(ping.parent_ping)

    def test_str_representation(self):
        ping = Ping.objects.create(user=self.user, latitude=10.0, longitude=20.0)
        self.assertIn(self.user.email, str(ping))
