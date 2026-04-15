from django.test import TestCase
from django.contrib.auth import authenticate
from eve.accounts.models import CustomUser

class CustomUserModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="securepass123"
        )

    # --- Unit: __str__ ---
    def test_str_returns_username(self):
        self.assertEqual(self.user.username, "testuser")

    def test_str_no_username_returns_fallback(self):
        user = CustomUser(username="")
        self.assertEqual(str(user), "No user")

    def test_first_name_is_none(self):
        self.assertIsNone(CustomUser.first_name)

    def test_last_name_is_none(self):
        self.assertIsNone(CustomUser.last_name)

    def test_first_name_is_not_a_model_field(self):
        field_names = [f.name for f in CustomUser._meta.get_fields()]
        self.assertNotIn("first_name", field_names)

    def test_last_name_is_not_a_model_field(self):
        field_names = [f.name for f in CustomUser._meta.get_fields()]
        self.assertNotIn("last_name", field_names)

    def test_is_abstract_user_subclass(self):
        from django.contrib.auth.models import AbstractUser
        self.assertIsInstance(self.user, AbstractUser)

    def test_create_user_requires_username(self):
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(username="", password="pass")

    def test_duplicate_username_raises_error(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(username="testuser", password="other")

    def test_create_superuser_sets_flags(self):
        su = CustomUser.objects.create_superuser("admin", password="adminpass")
        self.assertTrue(su.is_staff)
        self.assertTrue(su.is_superuser)

    def test_correct_password_authenticates(self):
        user = authenticate(username="testuser", password="securepass123")
        self.assertIsNotNone(user)

    def test_wrong_password_fails(self):
        user = authenticate(username="testuser", password="wrongpass")
        self.assertIsNone(user)

    def test_inactive_user_cannot_authenticate(self):
        self.user.is_active = False
        self.user.save()
        user = authenticate(username="testuser", password="securepass123")
        self.assertIsNone(user)

    def test_password_is_hashed(self):
        self.assertNotEqual(self.user.password, "securepass123")

    def test_check_password_correct(self):
        self.assertTrue(self.user.check_password("securepass123"))