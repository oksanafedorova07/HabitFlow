from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from habits.models import Habit

# Create your tests here.


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="habituser", password="testpass"
        )

    def test_cannot_set_reward_and_related_habit(self):
        habit1 = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="12:00",
            action="Читать",
            is_pleasant=True,
            duration=60,
        )
        habit2 = Habit(
            user=self.user,
            place="Дом",
            time="13:00",
            action="Учить",
            related_habit=habit1,
            reward="Шоколад",
            duration=60,
        )
        with self.assertRaises(ValidationError):
            habit2.clean()

    def test_duration_cannot_be_more_than_120(self):
        habit = Habit(
            user=self.user, place="Дом", time="14:00", action="Бегать", duration=121
        )
        with self.assertRaises(ValidationError):
            habit.clean()

    def test_public_habits(self):
        Habit.objects.create(
            user=self.user,
            place="Парк",
            time="15:00",
            action="Гулять",
            is_public=True,
            duration=60,
        )
        Habit.objects.create(
            user=self.user,
            place="Дом",
            time="16:00",
            action="Читать",
            is_public=False,
            duration=60,
        )
        public_habits = Habit.objects.filter(is_public=True)
        self.assertEqual(public_habits.count(), 1)
        self.assertEqual(public_habits.first().action, "Гулять")
