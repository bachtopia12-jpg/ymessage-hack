# Dockerfile

FROM python:3.10

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers
COPY . .

# Exposer le port utilisé par Flask
EXPOSE 5000

# Lancer l’application
CMD ["python", "main.py"]
