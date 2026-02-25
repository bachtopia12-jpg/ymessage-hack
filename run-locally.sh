#!/bin/bash
docker pull registry.gitlab.com/bachirou/ymessage-hack:latest
docker run -d -p 5000:5000 --name ymessage-chat registry.gitlab.com/bachirou/ymessage-hack:latest
echo "Application disponible sur http://localhost:5000"