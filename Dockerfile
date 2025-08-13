FROM python:3.11-slim as backend

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt.lists/*

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Обновление pip
RUN pip install --upgrade pip

# Build arguments с безопасными значениями по умолчанию (для CI)
ARG SECRET_KEY=django-insecure-ci-key-change-in-production
ARG DEBUG=false
ARG DB_NAME=habitflow_db
ARG DB_USER=postgres
ARG DB_PASSWORD=postgres
ARG DB_HOST=db
ARG DB_PORT=5432
ARG CELERY_BROKER_URL=redis://redis:6379/0
ARG CELERY_RESULT_BACKEND=redis://redis:6379/0
ARG TELEGRAM_BOT_TOKEN=test_token

# Экспортируем в переменные окружения
ENV DEBUG=$DEBUG
ENV DB_PORT=$DB_PORT

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Создаём временный .env только для сборки
ENV ENV_FILE_PATH=/tmp/.build-env
RUN echo "DEBUG=${DEBUG}" > /tmp/.build-env && \
    echo "DB_NAME=${DB_NAME}" >> /tmp/.build-env && \
    echo "DB_USER=${DB_USER}" >> /tmp/.build-env && \
    echo "DB_PASSWORD=${DB_PASSWORD}" >> /tmp/.build-env && \
    echo "DB_HOST=${DB_HOST}" >> /tmp/.build-env && \
    echo "DB_PORT=${DB_PORT}" >> /tmp/.build-env && \
    echo "CELERY_BROKER_URL=${CELERY_BROKER_URL}" >> /tmp/.build-env && \
    echo "CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}" >> /tmp/.build-env && \
    echo "TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}" >> /tmp/.build-env

# Собираем статику
RUN python manage.py collectstatic --noinput --skip-checks

# Удаляем временный файл
RUN rm -f /tmp/.build-env

# Команда по умолчанию
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

# Стадия: celery
FROM backend as celery

# Celery worker запускается с этой командой
CMD ["celery", "-A", "config", "worker", "-l", "info"]
