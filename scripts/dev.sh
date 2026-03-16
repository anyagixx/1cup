#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    log_info "Остановка сервисов..."
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

start_backend() {
    log_step "Запуск Backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        log_info "Создание виртуального окружения..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -q -r requirements.txt
    
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/1c_console"
    export REDIS_URL="redis://localhost:6379/0"
    
    log_info "Backend запущен на http://localhost:8000"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    cd ..
}

start_frontend() {
    log_step "Запуск Frontend..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        log_info "Установка зависимостей..."
        npm install
    fi
    
    log_info "Frontend запущен на http://localhost:3000"
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
}

start_services() {
    log_info "Запуск в режиме разработки..."
    
    if ! command -v python3 >/dev/null; then
        log_error "Python 3 не установлен"
        exit 1
    fi
    
    if ! command -v node >/dev/null; then
        log_error "Node.js не установлен"
        exit 1
    fi
    
    if ! command -v psql >/dev/null; then
        log_warn "PostgreSQL клиент не найден"
    fi
    
    if [ ! -f .env ]; then
        log_warn ".env не найден, создаём из примера..."
        cp .env.example .env
    fi
    
    log_step "Запуск зависимых сервисов (PostgreSQL, Redis)..."
    docker compose up -d postgres redis 2>/dev/null || {
        log_warn "Не удалось запустить PostgreSQL/Redis через Docker"
        log_warn "Убедитесь, что PostgreSQL и Redis запущены локально"
    }
    
    sleep 3
    
    start_backend
    start_frontend
    
    echo ""
    log_info "=========================================="
    log_info "  Режим разработки запущен!"
    log_info "=========================================="
    echo ""
    log_info "Backend:  http://localhost:8000"
    log_info "Frontend: http://localhost:3000"
    log_info "API Docs: http://localhost:8000/docs"
    echo ""
    log_info "Нажмите Ctrl+C для остановки"
    
    wait
}

start_services
