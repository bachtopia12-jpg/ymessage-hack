#!/bin/bash

API_KEY="$RENDER_API_KEY"  
SERVICE_NAME="chat-web-app"

curl -X POST "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "'$SERVICE_NAME'",
    "type": "web_service",
    "image": "registry.gitlab.com/daphnee.bouyedi641/chat-web-app:latest",
    "plan": "free"
  }'

echo "L'application est en train de se déployer sur Render !"