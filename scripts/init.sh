#!/bin/bash
set -e

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

generate_secret() {
    openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1
}

create_env_file() {
    if [ -f .env ]; then
        log_warn ".env файл уже существует"
        read -p "Перезаписать? [y/N] " confirm
        [ "$confirm" = "y" ] || return 0
    fi
    
    log_step "Создание .env файла..."
    
    SECRET_KEY=$(generate_secret)
    JWT_SECRET_KEY=$(generate_secret)
    
    cat > .env << EOF
# 1C Web Console Configuration
# Generated on $(date)

# Application secrets
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# 1C Cluster settings
RAC_EXECUTABLE=/opt/1cv8/x86_64/8.3.23.1739/rac
RAC_CLUSTER_HOST=localhost
RAC_CLUSTER_PORT=1545

# Database (optional override)
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/1c_console

# Redis (optional override)
# REDIS_URL=redis://localhost:6379/0
EOF
    
    log_info ".env файл создан"
}

wait_for_postgres() {
    log_step "Ожидание запуска PostgreSQL..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
            log_info "PostgreSQL готов"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    log_error "PostgreSQL не запустился"
    return 1
}

wait_for_backend() {
    log_step "Ожидание запуска Backend..."
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            log_info "Backend готов"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    log_error "Backend не запустился"
    return 1
}

create_admin_user() {
    log_step "Создание администратора..."
    
    docker compose exec -T backend python3 << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '/app')

from app.database.session import async_session_maker
from app.database.models import User
from app.auth.service import hash_password

async def create_admin():
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("Admin user already exists")
            return
        
        admin = User(
            username="admin",
            email="admin@localhost",
            hashed_password=hash_password("admin"),
            full_name="Administrator",
            role="admin",
            is_active=True,
            is_superuser=True,
        )
        session.add(admin)
        await session.commit()
        print("Admin user created successfully")

asyncio.run(create_admin())
PYEOF
}

main() {
    log_info "Инициализация 1C Web Console..."
    echo ""
    
    create_env_file
    
    log_step "Проверка Docker..."
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker не запущен"
        exit 1
    fi
    
    log_step "Сборка и запуск контейнеров..."
    docker compose up -d --build
    
    wait_for_postgres
    wait_for_backend
    
    create_admin_user
    
    echo ""
    log_info "=========================================="
    log_info "  1C Web Console успешно инициализирован!"
    log_info "=========================================="
    echo ""
    log_info "URL: http://localhost"
    log_info "API Docs: http://localhost:8000/docs"
    log_info "Логин: admin"
    log_info "Пароль: admin"
    echo ""
    log_warn "⚠️  Смените пароль администратора после первого входа!"
}

main "$@"
