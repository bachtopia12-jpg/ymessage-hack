#!/bin/bash

RENDER_SERVICE_NAME="chat-web-app"
DOCKER_IMAGE="registry.gitlab.com/daphnee.bouyedi641/chat-web-app:$CI_COMMIT_SHORT_SHA"
TIMEOUT=30

if [ -z "$RENDER_API_KEY" ]; then
  echo "ERREUR: RENDER_API_KEY non définie"
  exit 1
fi

SERVICE_RESPONSE=$(curl --max-time $TIMEOUT -s -X GET \
  "https://api.render.com/v1/services?name=$RENDER_SERVICE_NAME" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $RENDER_API_KEY")

if [ $? -ne 0 ]; then
  echo "Échec de la requête API"
  exit 1
fi

SERVICE_ID=$(echo "$SERVICE_RESPONSE" | jq -r '.[0].id')

if [ -z "$SERVICE_ID" ] || [ "$SERVICE_ID" == "null" ]; then
  echo "Création d'un nouveau service..."
  API_RESPONSE=$(curl --max-time $TIMEOUT -X POST "https://api.render.com/v1/services" \
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
  echo "Mise à jour du service $SERVICE_ID..."
  API_RESPONSE=$(curl --max-time $TIMEOUT -X PATCH \
    "https://api.render.com/v1/services/$SERVICE_ID" \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"image": "'$DOCKER_IMAGE'"}')
fi

if echo "$API_RESPONSE" | jq -e '.error' >/dev/null; then
  echo "Erreur: $(echo "$API_RESPONSE" | jq -r '.error')"
  exit 1
else
  echo "Succès!"
  echo "Vérifiez sur: https://dashboard.render.com"
fi