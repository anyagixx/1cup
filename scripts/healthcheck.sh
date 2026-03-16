#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SILENT=false

for arg in "$@"; do
    case $arg in
        --silent|-s) SILENT=true ;;
    esac
done

log_info() { $SILENT || echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { $SILENT || echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

check_service() {
    local name=$1
    local url=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url" >/dev/null 2>&1; then
            log_info "$name: OK"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    log_error "$name: FAILED (timeout after ${max_attempts}s)"
    return 1
}

main() {
    $SILENT || echo "Проверка статуса 1C Web Console..."
    $SILENT || echo ""
    
    FAILED=0
    
    if ! docker compose ps >/dev/null 2>&1; then
        log_error "Docker Compose не запущен"
        exit 1
    fi
    
    check_service "Backend API" "http://localhost:8000/health" 30 || FAILED=1
    check_service "Frontend" "http://localhost" 10 || FAILED=1
    
    $SILENT || echo ""
    
    if [ $FAILED -eq 0 ]; then
        $SILENT || log_info "Все сервисы работают"
        $SILENT || echo ""
        $SILENT || echo "Откройте http://localhost в браузере"
        exit 0
    else
        $SILENT || log_error "Некоторые сервисы недоступны"
        $SILENT || echo "Попробуйте: make logs"
        exit 1
    fi
}

main "$@"
