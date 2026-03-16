# 1C Web Console

Веб-консоль для управления кластером 1С:Предприятие 8.3.x на Ubuntu.

## Быстрый старт

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd 1c-web-console

# Первый запуск (автоматическая установка и инициализация)
./start.sh init

# Или вручную:
./start.sh install   # Проверка зависимостей
./start.sh init      # Инициализация

# Готово! Откройте http://localhost
# Логин: admin / Пароль: admin
```

## Команды управления

```bash
./start.sh              # Запуск сервисов
./start.sh start        # Запуск сервисов
./start.sh stop         # Остановка сервисов
./start.sh restart      # Перезапуск
./start.sh status       # Статус
./start.sh logs         # Все логи
./start.sh logs backend # Логи backend
./start.sh logs frontend# Логи frontend
./start.sh dev          # Режим разработки
./start.sh build        # Сборка Docker образов
./start.sh shell        # Shell в контейнере backend
./start.sh backup       # Резервная копия БД
./start.sh clean        # Очистка (удаление данных)
./start.sh help         # Справка
```

## Или через Makefile

```bash
make start     # Запуск
make stop      # Остановка
make logs      # Логи
make status    # Статус
make dev       # Режим разработки
make shell     # Shell backend
make backup    # Резервная копия
make clean     # Очистка
```

## Возможности

- 📊 **Дашборд** — обзор состояния кластера
- 🖥️ **Серверы** — управление серверами и процессами
- 💾 **Базы данных** — CRUD операции с информационными базами
- 👥 **Сеансы** — просмотр и завершение сеансов пользователей
- 📝 **Логи** — просмотр журнала событий с экспортом
- ⚡ **Real-time** — WebSocket обновления

## Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.11, FastAPI |
| Frontend | React 18, TypeScript, Ant Design |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Auth | JWT |
| 1C Integration | rac CLI utility |

## Требования

- Docker & Docker Compose
- 1C:Предприятие 8.3.x с rac utility

## Конфигурация

Файл `.env` создаётся автоматически при инициализации:

```env
# Секреты (генерируются автоматически)
SECRET_KEY=...
JWT_SECRET_KEY=...

# 1C Cluster
RAC_EXECUTABLE=/opt/1cv8/x86_64/8.3.23.1739/rac
RAC_CLUSTER_HOST=localhost
RAC_CLUSTER_PORT=1545
```

## API документация

После запуска:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Разработка

```bash
# Режим разработки (локально без Docker)
./start.sh dev

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## Структура проекта

```
1c-web-console/
├── backend/           # Python FastAPI
│   ├── app/
│   │   ├── api/      # REST endpoints
│   │   ├── auth/     # Аутентификация
│   │   ├── database/ # Модели БД
│   │   ├── rac/      # 1C RAC адаптер
│   │   └── ...
│   └── Dockerfile
├── frontend/          # React TypeScript
│   ├── src/
│   │   ├── api/      # API клиент
│   │   ├── auth/     # Auth context
│   │   ├── pages/    # Страницы
│   │   └── ...
│   └── Dockerfile
├── scripts/           # Скрипты автоматизации
├── docs/              # GRACE документация
├── docker-compose.yml
├── Makefile
├── start.sh           # Главный скрипт
└── README.md
```

## Лицензия

MIT
