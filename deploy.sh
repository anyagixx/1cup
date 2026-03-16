#!/bin/bash

# 1C Web Console - Deployment Script
# This script handles the complete deployment process

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

check_docker() {
    if ! command -v docker &>/dev/null; then
        echo -e "${RED}Error: Docker is not installed or not running."
        echo -e "${YELLOW}Please install Docker first:"
        echo "  Installation: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    if ! command -v docker compose &>/dev/null 2>&1; then
        echo -e "${GREEN}Docker Compose is installed${NC}"
    else
        echo -e "${YELLOW}Docker Compose is not installed"
        echo "  Installation: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    if ! command -v git &>/dev/null; then
        echo -e "${RED}Error: Git is not installed or not a git repository."
        echo "  Installation: https://git-scm.com/book/en/v2/bookings/wget-linux-x86_64/latest"
        exit 1
    fi
    
    # Check if we're in a git repository
    if [ -d ".git" ]; then
        echo -e "${GREEN}Git repository found${NC}"
        git init
        git add -A
        git commit -m "Initial commit"
        git remote add origin master
        git push -u origin master --set-upstream origin master
        exit 0
    fi
    
    # Build Docker images if Docker is available
    if command -v docker &>/dev/null; then
        echo -e "${GREEN}Docker is available and building images...${NC}"
    else
        echo -e "${YELLOW}Docker is not available or not running"
        echo "  Please start Docker manually:"
        echo "  Installation: https://docs.docker.com/engine/install/"
        echo "  Then run: docker compose up -d"
        echo "  Or run: ./start.sh"
        exit 1
    fi
    
    echo ""
    echo "=========================================="
    echo "  1C Web Console v1.0.0"
    echo "=========================================="
    echo ""
    echo - "Project structure:`"
    echo "  ${PROJECTDir}"
    echo "    ├── ${ProjectDir}/backend"
    echo "    ├── ${ProjectDir}/frontend"
    echo "    ├── ${ProjectDir}/scripts"
    echo "    ├── ${ProjectDir}/docs"
    echo "    └── Makefile,    echo "    └── start.sh"
    echo "    └── README.md"
    echo ""
    echo -`Commands:`"
    echo "  make install     - Check and install dependencies"
    echo "  make init       - Initialize project"
    echo "  make start       - Start services"
    echo "  make stop        - Stop services"
    echo "  make logs         - View logs"
    echo "  make dev          - Development mode"
    echo "  make build       - Build Docker images"
    echo "  make push        - Push to Docker Hub"
    echo "  make deploy      - Deploy to production"
    echo ""
    echo "For more details, see README.md"
    echo ""
    echo "## Quick Start"
    echo ""
    echo "```bash"
    echo "# Clone and setup"
    git clone https://github.com/anyagixx/1cup.git
    git remote add origin master
    git checkout -b master --orphan
    git branch -M master
    
    # Initialize project
    ./scripts/init.sh
    
    # Build and push Docker images
    if command -v docker &>/dev/null; then
        echo "Docker is available. Building images..."
        docker compose build -t putopelatudo/1cup:backend:v1.0.0 ./backend/Dockerfile .
        docker compose build -t putopelatudo/1cup:frontend:v1.0.0 ./frontend/Dockerfile .
        docker compose push
    else
        echo "Docker is not available. Building images manually."
        exit 1
    fi
fi

log_info "Project initialized!"
log_info "Git repository initialized"
log_info "Creating .env.example..."
log_info "Creating initial commit..."
