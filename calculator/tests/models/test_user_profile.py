from django.test import TestCase
from django.contrib.auth.models import User
from calculator.models import UserProfile


class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_user_profile_creation(self):
        user_profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(user_profile.user.username, 'testuser')

    def test_user_profile_balance_default(self):
        user_profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(user_profile.balance, 2500)

    def test_user_profile_on_user_delete(self):
        user_profile = UserProfile.objects.create(user=self.user)
        self.user.delete()
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(pk=user_profile.pk)
