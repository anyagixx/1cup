#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
    echo "1C Web Console - Управление кластером 1С:Предприятие"
    echo ""
    echo "Использование: $0 [команда]"
    echo ""
    echo "Команды:"
    echo "  start       Запуск сервисов (по умолчанию)"
    echo "  stop        Остановка сервисов"
    echo "  restart     Перезапуск сервисов"
    echo "  status      Статус сервисов"
    echo "  logs        Просмотр логов [backend|frontend]"
    echo "  init        Инициализация (первый запуск)"
    echo "  dev         Режим разработки"
    echo "  build       Сборка Docker образов"
    echo "  clean       Очистка (удаление данных)"
    echo "  shell       Вход в shell контейнера backend"
    echo "  backup      Резервное копирование БД"
    echo "  help        Эта справка"
    echo ""
    echo "Примеры:"
    echo "  $0              # Запуск"
    echo "  $0 start        # Запуск"
    echo "  $0 logs backend # Логи backend"
}

check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker не запущен"
        exit 1
    fi
}

start_services() {
    check_docker
    log_info "Запуск 1C Web Console..."
    docker compose up -d
    sleep 3
    ./scripts/healthcheck.sh --silent || true
    echo ""
    log_info "Сервисы запущены!"
    echo ""
    echo "  Web:  http://localhost"
    echo "  API:  http://localhost:8000/docs"
    echo "  User: admin / admin"
}

stop_services() {
    log_info "Остановка 1C Web Console..."
    docker compose down
    log_info "Сервисы остановлены"
}

restart_services() {
    stop_services
    start_services
}

show_status() {
    docker compose ps
    echo ""
    ./scripts/healthcheck.sh
}

show_logs() {
    SERVICE=$1
    if [ -n "$SERVICE" ]; then
        docker compose logs -f "$SERVICE"
    else
        docker compose logs -f
    fi
}

init_project() {
    log_info "Инициализация проекта..."
    ./scripts/install.sh
    ./scripts/init.sh
}

dev_mode() {
    log_info "Запуск в режиме разработки..."
    ./scripts/dev.sh
}

build_images() {
    check_docker
    log_info "Сборка Docker образов..."
    docker compose build --no-cache
    log_info "Образы собраны"
}

clean_all() {
    log_warn "⚠️  Это удалит все данные (БД, Redis, тома)!"
    read -p "Продолжить? [y/N] " confirm
    [ "$confirm" = "y" ] || exit 0
    
    docker compose down -v --remove-orphans
    docker system prune -f
    log_info "Очистка завершена"
}

shell_backend() {
    docker compose exec backend /bin/bash
}

backup_db() {
    mkdir -p backups
    BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"
    docker compose exec -T postgres pg_dump -U postgres 1c_console > "$BACKUP_FILE"
    log_info "Резервная копия создана: $BACKUP_FILE"
}

case "${1:-start}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    init)
        init_project
        ;;
    dev)
        dev_mode
        ;;
    build)
        build_images
        ;;
    clean)
        clean_all
        ;;
    shell)
        shell_backend
        ;;
    backup)
        backup_db
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Неизвестная команда: $1"
        show_help
        exit 1
        ;;
esac
