FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt.lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Обновление pip
RUN pip install --upgrade pip

# Переменные окружения (для сборки)
ARG SECRET_KEY
ARG DEBUG=false
ENV DEBUG=$DEBUG
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT=5432
ENV DB_PORT=$DB_PORT
ARG CELERY_BROKER_URL
ARG CELERY_RESULT_BACKEND
ARG TELEGRAM_BOT_TOKEN
# Добавьте другие, если нужно

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Собираем статику (теперь переменные доступны через ARG → в .env)
RUN mkdir -p .docker && \
    echo "SECRET_KEY=${SECRET_KEY}" > .docker/.env-build && \
    echo "DEBUG=${DEBUG}" >> .docker/.env-build && \
    echo "DB_NAME=${DB_NAME}" >> .docker/.env-build && \
    echo "DB_USER=${DB_USER}" >> .docker/.env-build && \
    echo "DB_PASSWORD=${DB_PASSWORD}" >> .docker/.env-build && \
    echo "DB_HOST=${DB_HOST}" >> .docker/.env-build && \
    echo "DB_PORT=${DB_PORT}" >> .docker/.env-build && \
    echo "CELERY_BROKER_URL=${CELERY_BROKER_URL}" >> .docker/.env-build && \
    echo "CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}" >> .docker/.env-build && \
    echo "TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}" >> .docker/.env-build

# Указываем environs читать временный файл
ENV ENV_FILE_PATH=.docker/.env-build

# Собираем статику
RUN python manage.py collectstatic --noinput

# Убираем временный .env (опционально, для безопасности)
RUN rm -rf .docker

# Команда по умолчанию
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

