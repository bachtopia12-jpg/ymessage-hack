# 💬 chat-web-app

Application de chat en temps réel construite avec **Python**, **Flask**, **Socket.IO**, **HTML**, **CSS**, et **JavaScript**.

## 🔧 Technologies utilisées

- Python 3.13  
- Flask  
- Flask-SocketIO  
- Docker  
- GitLab CI/CD  
- Render (déploiement automatique)

## 🧪 Lancer l'application en local

1. Installer les dépendances :

```bash
pip install Flask flask-socketio
Lancer l'application :

bash
Copier
Modifier
python main.py
Accéder à l'application :

http://127.0.0.1:5000

🐳 Lancer l’application avec Docker
Construire l’image Docker :

bash
Copier
Modifier
docker build -t chat-web-app .
Lancer le conteneur :

bash
Copier
Modifier
docker run -p 5000:5000 chat-web-app
L’application sera accessible sur http://localhost:5000

☁️ Déploiement automatique (Render + GitLab CI/CD)
Le projet est déployé automatiquement sur Render via GitLab CI/CD.

Fonctionnement :
À chaque git push, GitLab déclenche un pipeline.

Le script deploy.sh envoie la dernière image Docker vers Render.

Render met à jour automatiquement le service.

Lien de l’application en ligne :
🔗 https://chat-web-app.onrender.com (à remplacer par ton lien réel si besoin)

📂 Arborescence du projet
cpp
Copier
Modifier
chat-web-app/
├── main.py
├── templates/
├── static/
├── Dockerfile
├── .gitlab-ci.yml
├── deploy.sh
└── README.md
🚀 Phase 4 – Automatisation du déploiement
Objectif :
Déployer automatiquement l’application Dockerisée après chaque modification.

Étapes réalisées :
✅ Modification du pipeline .gitlab-ci.yml pour déployer sur Render.

✅ Écriture d’un script Bash deploy.sh pour envoyer l’image Docker.

✅ Test du déploiement en poussant un nouveau commit.

Pour tester le déploiement :
bash
Copier
Modifier
git add .
git commit -m "Test auto-deploy via pipeline"
git push
Puis :

Aller dans GitLab → CI/CD > Pipelines et vérifier que le pipeline se déclenche.

Aller sur Render → Vérifier si le service est mis à jour.

Si tout fonctionne, la Phase 4 est validée 🎉

 Auteur
Daphnée Bouyedi
MAYOUMA Johon Micael
Projet académique – Flash Chat Web App

yaml
Copier
Modifier

---
