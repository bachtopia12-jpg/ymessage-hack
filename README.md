# Ymessage Chat

Ymessage Chat est une application de messagerie instantanée permettant de discuter en temps réel via des salons publics ou privés. Le projet utilise Python avec le framework Flask et Socket.IO pour la communication bidirectionnelle.

## Technologies

- Langage : Python 3
- Framework Web : Flask
- Communication : Flask-SocketIO
- Base de données : SQLite
- Conteneurisation : Docker
- CI/CD : GitLab CI

## Installation et lancement

### Configuration locale

1. Installation des dépendances nécessaires :
   ```bash
   pip install -r requirements.txt
   ```

2. Lancement du serveur :
   ```bash
   python main.py
   ```

3. L'application est ensuite accessible à l'adresse suivante :
   http://127.0.0.1:5000

### Utilisation avec Docker

Il est également possible de lancer le projet via Docker :
```bash
docker build -t ymessage-chat .
docker run -p 5000:5000 ymessage-chat
```

## Fonctionnalités

- Système d'authentification (inscription et connexion)
- Personnalisation du profil avec gestion d'avatars
- Messagerie instantanée en temps réel
- Création de salons de discussion
- Gestion de liste d'amis et de demandes d'ajout
- Transfert de fichiers (images, audio, PDF)
- Support des appels vidéo via WebRTC

## Structure du projet

- main.py : Point d'entrée de l'application et gestion des événements Socket.IO.
- database.py : Gestion des modèles et de la base de données SQLite.
- templates/ : Fichiers HTML pour l'interface utilisateur.
- static/ : Ressources statiques (CSS, JavaScript, images, uploads).
- Dockerfile / docker-compose.yml : Configuration pour le déploiement conteneurisé.
- .gitlab-ci.yml : Pipeline de déploiement continu.

## Liens

- GitHub : https://github.com/bachtopia12-jpg
- GitLab : https://gitlab.com/bachirou
