#!/bin/bash
docker pull registry.gitlab.com/daphnee.bouyedi641/chat-web-app:latest
docker run -d -p 5000:5000 --name chat-app registry.gitlab.com/daphnee.bouyedi641/chat-web-app:latest
echo "App running on http://localhost:5000"