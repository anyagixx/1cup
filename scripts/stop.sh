#!/bin/bash

cd /opt/1c-web-console

docker compose -f docker-compose.standalone.yml down

echo "1C Web Console остановлена"
