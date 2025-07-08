from celery import shared_task
from django.conf import settings
from telegram import Bot


@shared_task
def send_telegram_reminder(telegram_id, message):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=telegram_id, text=message)
