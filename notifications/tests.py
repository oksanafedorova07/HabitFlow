from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from habits.models import Habit
from notifications.models import UserProfile
from notifications.periodic import check_and_send_habit_reminders

# Create your tests here.


class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        response = self.client.get("/api/notifications/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("telegram_id", response.data)

    def test_update_telegram_id(self):
        response = self.client.patch(
            "/api/notifications/profile/", {"telegram_id": "123456789"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.telegram_id, "123456789")


class HabitReminderTaskTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="reminderuser", password="testpass"
        )
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.telegram_id = "123456789"
        self.profile.save()
        now = timezone.localtime()
        self.habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time=now.time().replace(second=0, microsecond=0),
            action="Выпить воду",
            is_active=True,
            days_of_week=str(now.weekday()),
            duration=60,
        )

    @patch("notifications.tasks.send_telegram_reminder.delay")
    def test_reminder_sent(self, mock_send):
        check_and_send_habit_reminders()
        mock_send.assert_called_once_with(
            "123456789",
            f'Напоминание: Выпить воду в Дом ({self.habit.time.strftime("%H:%M")})',
        )
