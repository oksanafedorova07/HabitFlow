from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.


class Habit(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=255, verbose_name="Действие")
    is_pleasant = models.BooleanField(default=False, verbose_name="Приятная привычка")
    related_habit = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Связанная привычка",
    )
    period = models.PositiveSmallIntegerField(
        default=1, verbose_name="Периодичность (дни)"
    )
    reward = models.CharField(max_length=255, blank=True, verbose_name="Вознаграждение")
    duration = models.PositiveSmallIntegerField(
        verbose_name="Время на выполнение (сек)"
    )
    is_public = models.BooleanField(default=False, verbose_name="Публичная привычка")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    days_of_week = models.CharField(
        max_length=13, blank=True, verbose_name="Дни недели (через запятую, 0=Пн,6=Вс)"
    )

    def clean(self):
        # Исключить одновременный выбор связанной привычки и указания вознаграждения
        if self.related_habit and self.reward:
            raise ValidationError(
                "Нельзя одновременно указывать связанную привычку и вознаграждение."
            )
        # Время выполнения должно быть не больше 120 секунд
        if self.duration > 120:
            raise ValidationError("Время выполнения не может превышать 120 секунд.")
        # В связанные привычки могут попадать только привычки с признаком приятной привычки
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError(
                "В связанные привычки могут попадать только приятные привычки."
            )
        # У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )
        # Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if not (1 <= self.period <= 7):
            raise ValidationError("Периодичность должна быть от 1 до 7 дней.")

    def __str__(self):
        return f"{self.action} в {self.time} в {self.place}"

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-id"]
