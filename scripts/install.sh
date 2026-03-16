#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_docker() {
    if ! command_exists docker; then
        log_error "Docker не установлен"
        log_info "Установка Docker..."
        curl -fsSL https://get.docker.com | sh
        sudo usermod -aG docker "$USER"
        log_warn "Docker установлен. Выйдите и войдите снова, затем запустите скрипт повторно."
        exit 0
    fi
    log_info "Docker установлен: $(docker --version)"
}

check_docker_compose() {
    if docker compose version >/dev/null 2>&1; then
        log_info "Docker Compose установлен: $(docker compose version)"
    elif command_exists docker-compose; then
        log_info "docker-compose установлен: $(docker-compose --version)"
    else
        log_error "Docker Compose не установлен"
        exit 1
    fi
}

check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        log_info "Python $PYTHON_VERSION найден"
    else
        log_warn "Python 3 не найден (требуется только для режима разработки)"
    fi
}

check_nodejs() {
    if command_exists node; then
        NODE_VERSION=$(node --version)
        log_info "Node.js $NODE_VERSION найден"
    else
        log_warn "Node.js не найден (требуется только для режима разработки)"
    fi
}

check_1c_rac() {
    RAC_PATH="${RAC_EXECUTABLE:-/opt/1cv8/x86_64/8.3.23.1739/rac}"
    if [ -f "$RAC_PATH" ]; then
        log_info "1C rac utility найдена: $RAC_PATH"
    else
        log_warn "1C rac utility не найдена по пути: $RAC_PATH"
        log_warn "Укажите правильный путь в .env файле (RAC_EXECUTABLE)"
    fi
}

main() {
    log_info "Проверка зависимостей 1C Web Console..."
    echo ""
    
    check_docker
    check_docker_compose
    check_python
    check_nodejs
    check_1c_rac
    
    echo ""
    log_info "Все проверки пройдены!"
    log_info "Запустите 'make init' для инициализации проекта"
}

main "$@"
