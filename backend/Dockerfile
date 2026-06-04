# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
# Копируем содержимое папки backend в подпапку /app/backend, сохраняя структуру пакета
COPY . ./backend

EXPOSE 5000

# --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
# Запускаем Gunicorn, указывая на wsgi внутри пакета backend
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.wsgi:app"]