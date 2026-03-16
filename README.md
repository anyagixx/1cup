# 1C Web Console

Веб-консоль для управления кластером 1С:Предприятие 8.3.x.

## Быстрая установка

```bash
curl -fsSL https://raw.githubusercontent.com/anyagixx/1cup/main/install.sh | bash
```

Установщик спросит:
- IP сервера кластера 1С
- Порт кластера (по умолчанию 1545)
- Логин/пароль кластера (если есть)

После установки откройте: **http://IP-СЕРВЕРА:8080**

- **Логин:** admin
- **Пароль:** admin

## Возможности

| Функция | Описание |
|---------|----------|
| Dashboard | Обзор состояния кластера |
| Servers | Список серверов и процессов |
| Databases | Управление информационными базами |
| Sessions | Просмотр и завершение сеансов |
| Logs | Просмотр и экспорт логов |
| Settings | Системные настройки |
| Real-time | WebSocket для live updates |

## Команды управления

```bash
# Запуск
/opt/1c-web-console/start.sh

# Остановка
/opt/1c-web-console/stop.sh

# Перенастроить подключение к 1С
/opt/1c-web-console/reconfigure.sh

# Логи
cd /opt/1c-web-console && docker compose -f docker-compose.standalone.yml logs -f
```

## Требования

- Ubuntu 20.04+
- Установленный 1С:Предприятие 8.3.x
- Доступ к серверу кластера 1С

## Ручная установка

```bash
# Клонировать
git clone https://github.com/anyagixx/1cup.git /opt/1c-web-console
cd /opt/1c-web-console

# Создать .env
cp .env.example .env
nano .env

# Запустить
docker compose -f docker-compose.standalone.yml up -d
```

## API Endpoints

| Endpoint | Описание |
|----------|----------|
| `POST /api/auth/login` | Вход |
| `GET /api/cluster/status` | Статус кластера |
| `GET /api/servers` | Список серверов |
| `GET /api/databases` | Список баз данных |
| `GET /api/sessions` | Активные сеансы |
| `GET /api/logs` | Журнал событий |
| `WS /ws/events` | WebSocket события |

## Docker Hub

- `putopelatudo/1cup:backend-latest`
- `putopelatudo/1cup:frontend-latest`

## Лицензия

MIT
