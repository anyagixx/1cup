# 1C Web Console

Веб-консоль для управления кластером 1С:Предприятие 8.3.x на Ubuntu.

## Возможности

| Функция | Описание |
|---------|------------------------------------------------------------------|
| **Dashboard** — обзор состояния кластера, статист |
| **Servers** — список серверов и процессов |
    **Databases** — управление информационными базами
    **Sessions** — просмотр и завершение сеансов |
    **Logs** — просмотр и экспорт логов |
    **Settings** — систем настройки |
    **Real-time** — WebSocket для live updates |
| **Backup** — резервное копирование БД |

| **API** | `/api/auth/*` — аутентификация
    `/api/cluster/*` — информация о кластере
    `/api/cluster/status` — статус кластера
    `/api/servers/*` — список серверов
    `/api/servers/{id}/*` — детали сервера
    `/api/servers/{id}/process/*` — процессы сервера
    `/api/servers/restart` — перезапуск сервера
    `/api/databases` — CRUD для баз данных
    `/api/databases` — создание новой базы
    `/api/databases` — удал базы
    `/api/databases/{id}/backup/*` — резервное копирование
    `/api/databases/{id}/export/*` — экспорт логов (формат: CSV, JSON)
    `/api/logs` — просмотр логов
    `/api/logs/stream` — WebSocket streaming
    `/api/logs/export` — экспорт логов (формат: CSV, JSON)
    `/ws` — WebSocket endpoint
    `/health` — Health check
    `/` — Root endpoint
    `/api/auth/login` — Вход
    `/api/auth/logout` — Выход
    `/api/auth/refresh` — Обновление токена
    `/api/auth/me` — Текущийий пользователь
    `/api/auth/change-password` — Смена пароль
    `/api/auth/users` — Список пользователей (только admin)
    `/api/auth/users` — Созд пользователя
    `/api/auth/users/{id}` — Получ пользователя
    `/api/auth/users` — Обновить пользователя
    `/api/auth/users/{id}` — Удалить пользователя
    `/api/databases` — Список баз данных
    `/api/databases` — Создание новой базы
    `/api/databases` — удаление базы данных
    `/api/databases` — экспорт логов
    `/api/logs` — Получение журнала
    `/api/logs/stream` — WebSocket стриминг
    `/api/logs/export` — Экспорт логов
    `/api/sessions` — Активные сеансы
    `/api/sessions` — Завершить сеанса
    `/api/sessions/bulk-terminate` — Массовое завершение сеансов
    `/api/sessions/terminate-all` — Завершить всех сеансовов кластере
    `/ws/events` — WebSocket для real-time updates
    ```

## Запуск

```bash
# Первый запуск
./start.sh init

# Или через Docker
./start.sh start

# Режим разработки
./start.sh dev

# Очистка
./start.sh clean

# Или через Docker Compose
./start.sh start
./start.sh logs
./start.sh stop
./start.sh restart
./start.sh status
./start.sh shell
./start.sh backup
./start.sh build
./start.sh build
./start.sh dev
./start.sh clean
./start.sh logs [service]
./start.sh logs backend
./start.sh logs frontend
./start.sh status
./start.sh help
```

---

## Использование

1. **Убедитесь, что вы делите**:**Да** файл в `.env`** эти:
   - Проверьте `RAC_EXECUTABLE` path in `.env` (или использ `/opt/1cv8/x86_64/8.3.23.1739/rac`)
   - Проверьте установлен PostgreSQL и Redis (если you want to use them locally)
   - Pровер if Docker and Docker Compose are installed (run `make install` to skip tests)
   - PULL Docker images if needed
   - BUILD and push to Docker Hub

## Запуск

```bash
# Запуск
./start.sh

# Или
docker compose up -d
# или для разработки
docker compose build --no-cache
docker compose pull
docker compose up -d

# Откройте в браузере: http://localhost

# Логин: admin / Пароль: admin
# ⏠️ Смените пароль администратора после первого входа!

