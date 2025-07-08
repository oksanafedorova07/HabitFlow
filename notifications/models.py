from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="profile"
    )
    telegram_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"


class NotificationLog(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="notification_logs"
    )
    habit = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    telegram_id = models.CharField(max_length=64)

    def __str__(self):
        return f"Лог: {self.user} - {self.habit} - {self.sent_at}"
