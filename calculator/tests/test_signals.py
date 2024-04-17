from django.test import TestCase
from django.contrib.auth.models import User
from calculator.models import UserProfile


class UserSignalTests(TestCase):
    def test_create_user_creates_userprofile(self):
        # Test that creating a User also creates a UserProfile
        user = User.objects.create_user(username='testuser', password='12345')
        self.assertIsInstance(user.userprofile, UserProfile, "UserProfile should be created automatically.")

    def test_update_user_saves_userprofile(self):
        # Test that saving a User also saves the UserProfile
        user = User.objects.create_user(username='testuser', password='12345')
        user.first_name = "Test"
        user.save()

        # Attempt to fetch the updated UserProfile from the database
        profile = UserProfile.objects.get(user=user)
        self.assertIsNotNone(profile, "UserProfile should exist after updating User.")

    def test_userprofile_not_duplicated_on_user_update(self):
        # Ensure that updating a User does not duplicate the UserProfile
        user = User.objects.create_user(username='testuser', password='12345')
        user.first_name = "UpdatedName"
        user.save()

        profiles_count = UserProfile.objects.filter(user=user).count()
        self.assertEqual(profiles_count, 1, "Only one UserProfile should exist per user.")
