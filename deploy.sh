#!/bin/bash

RENDER_SERVICE_NAME="chat-web-app"
DOCKER_IMAGE="registry.gitlab.com/daphnee.bouyedi641/chat-web-app:$CI_COMMIT_SHORT_SHA"

SERVICE_ID=$(curl -s -X GET "https://api.render.com/v1/services?name=$RENDER_SERVICE_NAME" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $RENDER_API_KEY" | jq -r '.[0].id')

if [ -z "$SERVICE_ID" ] || [ "$SERVICE_ID" == "null" ]; then
  echo "Création d'un nouveau service sur Render..."
  curl -X POST "https://api.render.com/v1/services" \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "'$RENDER_SERVICE_NAME'",
      "type": "web_service",
      "image": "'$DOCKER_IMAGE'",
      "plan": "free",
      "env": "docker"
    }'
else
  echo "Mise à jour du service existant sur Render..."
  curl -X PATCH "https://api.render.com/v1/services/$SERVICE_ID" \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "image": "'$DOCKER_IMAGE'"
    }'
fi

echo "🎉 Déploiement terminé! Vérifiez sur https://dashboard.render.com"