FROM python:3.10-slim

# Configuration pour Python et les logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

WORKDIR /app

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du projet
COPY . .

# Création des dossiers nécessaires
RUN mkdir -p static/uploads static/avatars static/js

# Lancement avec Gunicorn et le worker eventlet pour Socket.IO
CMD gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:${PORT} main:app
