#!/bin/bash

cd /opt/1c-web-console

if [[ ! -f .env ]]; then
    echo "Ошибка: файл .env не найден"
    echo "Выполните установку: curl -fsSL https://raw.githubusercontent.com/anyagixx/1cup/main/install.sh | bash"
    exit 1
fi

echo "=== Перенастройка подключения к кластеру 1С ==="
echo ""
echo "Текущие настройки:"
echo "  IP кластера: $(grep RAC_CLUSTER_HOST .env | cut -d= -f2)"
echo "  Порт: $(grep RAC_CLUSTER_PORT .env | cut -d= -f2)"
echo "  Логин: $(grep RAC_CLUSTER_USER .env | cut -d= -f2)"
echo ""

read -p "Новый IP сервера кластера 1С: " NEW_HOST
if [[ -z "$NEW_HOST" ]]; then
    echo "IP обязателен"
    exit 1
fi

read -p "Новый порт кластера [1545]: " NEW_PORT
NEW_PORT=${NEW_PORT:-1545}

read -p "Логин кластера (Enter если без авторизации): " NEW_USER
if [[ -n "$NEW_USER" ]]; then
    read -s -p "Пароль кластера: " NEW_PASS
    echo ""
fi

sed -i "s|^RAC_CLUSTER_HOST=.*|RAC_CLUSTER_HOST=${NEW_HOST}|" .env
sed -i "s|^RAC_CLUSTER_PORT=.*|RAC_CLUSTER_PORT=${NEW_PORT}|" .env
sed -i "s|^RAC_CLUSTER_USER=.*|RAC_CLUSTER_USER=${NEW_USER}|" .env
if [[ -n "$NEW_PASS" ]]; then
    sed -i "s|^RAC_CLUSTER_PASSWORD=.*|RAC_CLUSTER_PASSWORD=${NEW_PASS}|" .env
fi

echo ""
echo "Настройки обновлены."
echo ""
read -p "Перезапустить сервис? [Y/n]: " RESTART
RESTART=${RESTART:-Y}

if [[ "$RESTART" =~ ^[YyДд]$ ]]; then
    docker compose -f docker-compose.standalone.yml down
    docker compose -f docker-compose.standalone.yml up -d
    echo ""
    echo "Сервис перезапущен"
fi
