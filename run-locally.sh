#!/bin/bash
docker pull registry.gitlab.com/bachirou/ymessage-hack:latest
docker run -d -p 5000:5000 --name ymessage-app registry.gitlab.com/bachirou/ymessage-hack:latest
echo "App running on http://localhost:5000"