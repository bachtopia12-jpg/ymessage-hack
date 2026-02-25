#!/bin/bash

# Configuration
RENDER_SERVICE_NAME="ymessage-hack"
DOCKER_IMAGE="registry.gitlab.com/bachirou/ymessage-hack:$CI_COMMIT_SHORT_SHA"
TIMEOUT=60

if [ -z "$RENDER_API_KEY" ]; then
  echo "Erreur : RENDER_API_KEY n'est pas configurée dans les variables CI/CD."
  exit 1
fi

echo "Recherche du service : $RENDER_SERVICE_NAME"
SERVICE_RESPONSE=$(curl -s -X GET \
  "https://api.render.com/v1/services?name=$RENDER_SERVICE_NAME" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $RENDER_API_KEY")

SERVICE_ID=$(echo "$SERVICE_RESPONSE" | jq -r '.[0].id // empty')

if [ -z "$SERVICE_ID" ] || [ "$SERVICE_ID" == "null" ]; then
  echo "Service non trouvé. Tentative de création d'un nouveau service..."
  API_RESPONSE=$(curl -s -X POST "https://api.render.com/v1/services" \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "'$RENDER_SERVICE_NAME'",
      "type": "web_service",
      "image": "'$DOCKER_IMAGE'",
      "plan": "free",
      "env": "docker"
    }')
else
  echo "Mise à jour du service existant (ID: $SERVICE_ID)..."
  API_RESPONSE=$(curl -s -X PATCH \
    "https://api.render.com/v1/services/$SERVICE_ID" \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"image": "'$DOCKER_IMAGE'"}')
fi

# Vérification du résultat
if echo "$API_RESPONSE" | jq -e '.error' >/dev/null; then
  echo "Erreur retournée par l'API Render :"
  echo "$API_RESPONSE" | jq -r '.error'
  exit 1
else
  echo "Déploiement lancé avec succès !"
fi