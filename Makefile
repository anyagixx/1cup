.PHONY: start stop restart logs dev install init clean status help build pull

COMPOSE := docker compose
BACKEND_CMD := cd backend && pip install -r requirements.txt -q && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
FRONTEND_CMD := cd frontend && npm install -q && npm run dev

help:
	@echo "1C Web Console - Команды управления"
	@echo ""
	@echo "  make install    - Проверка и установка зависимостей"
	@echo "  make init       - Инициализация (создание .env, admin пользователя)"
	@echo "  make start      - Запуск сервисов (Docker)"
	@echo "  make stop       - Остановка сервисов"
	@echo "  make restart    - Перезапуск сервисов"
	@echo "  make status     - Статус сервисов"
	@echo "  make logs       - Просмотр логов"
	@echo "  make dev        - Режим разработки (локально без Docker)"
	@echo "  make build      - Сборка Docker образов"
	@echo "  make pull       - Загрузка базовых образов"
	@echo "  make clean      - Очистка (удаление томов и кеша)"
	@echo "  make backup     - Резервное копирование БД"
	@echo "  make shell      - Вход в shell контейнера backend"
	@echo ""

install:
	@echo "Проверка зависимостей..."
	@./scripts/install.sh

init:
	@echo "Инициализация проекта..."
	@./scripts/init.sh

start:
	@echo "Запуск 1C Web Console..."
	@$(COMPOSE) up -d
	@echo "Ожидание запуска сервисов..."
	@./scripts/healthcheck.sh
	@echo ""
	@echo "✅ 1C Web Console запущена!"
	@echo "   Web интерфейс: http://localhost"
	@echo "   API документация: http://localhost:8000/docs"
	@echo "   Логин: admin / Пароль: admin"
	@echo ""

stop:
	@echo "Остановка сервисов..."
	@$(COMPOSE) down

restart: stop start

status:
	@$(COMPOSE) ps
	@echo ""
	@./scripts/healthcheck.sh --silent || echo "⚠️  Некоторые сервисы не запущены"

logs:
	@$(COMPOSE) logs -f

logs-backend:
	@$(COMPOSE) logs -f backend

logs-frontend:
	@$(COMPOSE) logs -f frontend

dev:
	@echo "Запуск в режиме разработки..."
	@./scripts/dev.sh

build:
	@echo "Сборка Docker образов..."
	@$(COMPOSE) build --no-cache

pull:
	@echo "Загрузка базовых образов..."
	@docker pull python:3.11-slim
	@docker pull node:20-alpine
	@docker pull nginx:alpine
	@docker pull postgres:15-alpine
	@docker pull redis:7-alpine

clean:
	@echo "⚠️  Это удалит все данные (БД, Redis, тома)!"
	@read -p "Продолжить? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@$(COMPOSE) down -v --remove-orphans
	@docker system prune -f
	@echo "Очистка завершена"

backup:
	@echo "Создание резервной копии БД..."
	@mkdir -p backups
	@docker exec 1c-web-console-postgres-1 pg_dump -U postgres 1c_console > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Резервная копия создана в папке backups/"

shell:
	@docker exec -it 1c-web-console-backend-1 /bin/bash

psql:
	@docker exec -it 1c-web-console-postgres-1 psql -U postgres -d 1c_console

redis-cli:
	@docker exec -it 1c-web-console-redis-1 redis-cli
