#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="/opt/1c-web-console"
COMPOSE_FILE="docker-compose.standalone.yml"

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║       1C Web Console Installer           ║"
    echo "║           Version 1.0.1                  ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${YELLOW}→${NC} $1"; }

check_root() {
    if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}Потребуется sudo для установки${NC}"
    fi
}

check_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker уже установлен ($(docker --version | cut -d' ' -f3 | tr -d ','))"
        return 0
    fi
    
    print_info "Установка Docker..."
    curl -fsSL https://get.docker.com | sh
    
    if command -v docker &> /dev/null; then
        print_success "Docker установлен"
    else
        print_error "Не удалось установить Docker"
        exit 1
    fi
}

start_docker() {
    if ! docker info &> /dev/null; then
        print_info "Запуск Docker..."
        sudo systemctl start docker
        sudo systemctl enable docker
        sleep 3
    fi
    print_success "Docker запущен"
}

ask_settings() {
    echo ""
    echo -e "${BLUE}Настройка подключения к кластеру 1С:${NC}"
    echo ""
    
    read -p "IP сервера кластера 1С [localhost]: " CLUSTER_HOST
    CLUSTER_HOST=${CLUSTER_HOST:-localhost}
    
    read -p "Порт кластера [1545]: " CLUSTER_PORT
    CLUSTER_PORT=${CLUSTER_PORT:-1545}
    
    read -p "Логин кластера (Enter если нет): " CLUSTER_USER
    
    if [[ -n "$CLUSTER_USER" ]]; then
        read -s -p "Пароль кластера: " CLUSTER_PASSWORD
        echo ""
    else
        CLUSTER_PASSWORD=""
    fi
    
    echo ""
    print_info "Проверка пути к rac..."
    
    RAC_PATH=""
    for path in "/opt/1cv8/x86_64" "/opt/1cv8"; do
        if [[ -d "$path" ]]; then
            RAC_VERSION=$(ls -1 "$path" 2>/dev/null | grep -E '^[0-9]+\.' | sort -V | tail -1)
            if [[ -n "$RAC_VERSION" && -f "$path/$RAC_VERSION/rac" ]]; then
                RAC_PATH="$path/$RAC_VERSION/rac"
                break
            fi
        fi
    done
    
    if [[ -z "$RAC_PATH" ]]; then
        read -p "Путь к rac [/opt/1cv8/x86_64/8.3.23.1739/rac]: " RAC_PATH
        RAC_PATH=${RAC_PATH:-/opt/1cv8/x86_64/8.3.23.1739/rac}
    else
        print_success "Найден rac: $RAC_PATH"
    fi
}

generate_secret() {
    openssl rand -hex 32 2>/dev/null || echo "change-this-secret-key-$(date +%s)"
}

create_files() {
    print_info "Создание директории $INSTALL_DIR..."
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown "$USER:$USER" "$INSTALL_DIR"
    
    cd "$INSTALL_DIR"
    
    SECRET_KEY=$(generate_secret)
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    print_info "Создание конфигурационных файлов..."
    
    cat > .env << EOF
# 1C Web Console Configuration
# Generated: $(date)

# 1C Cluster Settings
RAC_EXECUTABLE=${RAC_PATH}
RAC_CLUSTER_HOST=${CLUSTER_HOST}
RAC_CLUSTER_PORT=${CLUSTER_PORT}
RAC_CLUSTER_USER=${CLUSTER_USER}
RAC_CLUSTER_PASSWORD=${CLUSTER_PASSWORD}

# Security
SECRET_KEY=${SECRET_KEY}

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=1c_console
EOF
    
    cat > docker-compose.standalone.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-1c_console}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 10
    restart: unless-stopped
    networks:
      - 1c-console-net

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 10
    restart: unless-stopped
    networks:
      - 1c-console-net

  backend:
    image: putopelatudo/1cup:backend-latest
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@postgres:5432/${POSTGRES_DB:-1c_console}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      RAC_EXECUTABLE: ${RAC_EXECUTABLE}
      RAC_CLUSTER_HOST: ${RAC_CLUSTER_HOST}
      RAC_CLUSTER_PORT: ${RAC_CLUSTER_PORT}
      RAC_CLUSTER_USER: ${RAC_CLUSTER_USER}
      RAC_CLUSTER_PASSWORD: ${RAC_CLUSTER_PASSWORD}
      CORS_ORIGINS: '["http://localhost:8080","http://127.0.0.1:8080"]'
    volumes:
      - /opt/1cv8:/opt/1cv8:ro
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - 1c-console-net

  frontend:
    image: putopelatudo/1cup:frontend-latest
    ports:
      - "8080:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - 1c-console-net

volumes:
  postgres_data:
  redis_data:

networks:
  1c-console-net:
    driver: bridge
EOF

    cat > start.sh << 'STARTSCRIPT'
#!/bin/bash
cd /opt/1c-web-console
docker compose -f docker-compose.standalone.yml up -d
echo "1C Web Console запущена на http://localhost:8080"
STARTSCRIPT
    chmod +x start.sh

    cat > stop.sh << 'STOPSCRIPT'
#!/bin/bash
cd /opt/1c-web-console
docker compose -f docker-compose.standalone.yml down
echo "1C Web Console остановлена"
STOPSCRIPT
    chmod +x stop.sh

    cat > reconfigure.sh << 'RECONFSCRIPT'
#!/bin/bash
cd /opt/1c-web-console

echo "Текущие настройки:"
echo "  IP кластера: $(grep RAC_CLUSTER_HOST .env | cut -d= -f2)"
echo "  Порт: $(grep RAC_CLUSTER_PORT .env | cut -d= -f2)"
echo ""

read -p "Новый IP сервера кластера 1С: " NEW_HOST
read -p "Новый порт кластера [1545]: " NEW_PORT
NEW_PORT=${NEW_PORT:-1545}
read -p "Логин кластера (Enter если нет): " NEW_USER
if [[ -n "$NEW_USER" ]]; then
    read -s -p "Пароль кластера: " NEW_PASS
    echo ""
fi

sed -i "s|^RAC_CLUSTER_HOST=.*|RAC_CLUSTER_HOST=${NEW_HOST}|" .env
sed -i "s|^RAC_CLUSTER_PORT=.*|RAC_CLUSTER_PORT=${NEW_PORT}|" .env
sed -i "s|^RAC_CLUSTER_USER=.*|RAC_CLUSTER_USER=${NEW_USER}|" .env
sed -i "s|^RAC_CLUSTER_PASSWORD=.*|RAC_CLUSTER_PASSWORD=${NEW_PASS}|" .env

echo ""
echo "Настройки обновлены. Перезапустите сервис:"
echo "  ./stop.sh && ./start.sh"
RECONFSCRIPT
    chmod +x reconfigure.sh

    print_success "Конфигурационные файлы созданы"
}

pull_images() {
    print_info "Загрузка Docker образов..."
    docker compose -f docker-compose.standalone.yml pull
    print_success "Образы загружены"
}

start_services() {
    print_info "Запуск сервисов..."
    docker compose -f docker-compose.standalone.yml up -d
    
    sleep 5
    
    if docker compose -f docker-compose.standalone.yml ps | grep -q "running"; then
        print_success "Сервисы запущены"
    else
        print_error "Ошибка запуска сервисов"
        docker compose -f docker-compose.standalone.yml logs
        exit 1
    fi
}

print_final() {
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     Установка завершена успешно!         ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BLUE}Web-интерфейс:${NC} http://${SERVER_IP}:8080"
    echo ""
    echo -e "  ${YELLOW}Логин:${NC} admin"
    echo -e "  ${YELLOW}Пароль:${NC} admin"
    echo ""
    echo -e "  ${BLUE}Команды управления:${NC}"
    echo "    Запуск:     $INSTALL_DIR/start.sh"
    echo "    Остановка:  $INSTALL_DIR/stop.sh"
    echo "    Перенастройка: $INSTALL_DIR/reconfigure.sh"
    echo "    Логи:       cd $INSTALL_DIR && docker compose -f docker-compose.standalone.yml logs -f"
    echo ""
    echo -e "  ${RED}⚠ Смените пароль администратора после первого входа!${NC}"
    echo ""
}

main() {
    print_header
    check_root
    check_docker
    start_docker
    ask_settings
    create_files
    pull_images
    start_services
    print_final
}

main "$@"
