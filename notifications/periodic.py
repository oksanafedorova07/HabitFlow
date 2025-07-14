import logging

from celery import shared_task
from django.utils import timezone

from notifications.tasks import send_telegram_reminder

logger = logging.getLogger(__name__)


@shared_task
def check_and_send_habit_reminders():
    print("Задача check_and_send_habit_reminders запущена")
    try:
        now = timezone.localtime()
        print("now:", now)
        weekday = now.weekday()
        today = now.date()
        from habits.models import Habit  # импорт внутри задачи
        from notifications.models import NotificationLog

        print("Импорт моделей успешен")
        habits = Habit.objects.filter(
            is_active=True, time__hour=now.hour, time__minute=now.minute
        )
        print("habits:", habits)
        for habit in habits:
            if habit.days_of_week:
                days = [
                    int(d) for d in habit.days_of_week.split(",") if d.strip().isdigit()
                ]
                if weekday not in days:
                    continue
            if habit.period > 1:
                days_since = (today - habit.user.date_joined.date()).days
                if days_since % habit.period != 0:
                    continue
            user_profile = getattr(habit.user, "profile", None)
            if user_profile and user_profile.telegram_id:
                if habit.reward:
                    msg = f"{habit.action} в {habit.place} ({habit.time.strftime('%H:%M')}). После выполнения: {habit.reward}"
                elif habit.related_habit:
                    msg = f"{habit.action} в {habit.place} ({habit.time.strftime('%H:%M')}). После выполнения: {habit.related_habit.action}"
                else:
                    msg = f"Напоминание: {habit.action} в {habit.place} ({habit.time.strftime('%H:%M')})"
                send_telegram_reminder.delay(user_profile.telegram_id, msg)
                NotificationLog.objects.create(
                    user=habit.user,
                    habit=habit.action,
                    message=msg,
                    telegram_id=user_profile.telegram_id,
                )
    except Exception as e:
        print("Ошибка в check_and_send_habit_reminders:", e)
        import traceback

        traceback.print_exc()
        logger.exception(f"Ошибка в check_and_send_habit_reminders: {e}")
        raise
