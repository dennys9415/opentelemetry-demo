#!/bin/bash

# OpenTelemetry Demo Deployment Script
# Usage: ./scripts/deploy.sh [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
ENVIRONMENT=${1:-"development"}
PROJECT_NAME="opentelemetry-demo"
DOCKER_COMPOSE_FILE="docker-compose.yml"
DOCKER_COMPOSE_PROD_FILE="docker-compose.prod.yml"

# Validate environment
validate_environment() {
    case $ENVIRONMENT in
        development|staging|production)
            log_info "Deploying to $ENVIRONMENT environment"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            log_error "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f ".env.$ENVIRONMENT" ] && [ "$ENVIRONMENT" != "development" ]; then
        log_warning "Environment file .env.$ENVIRONMENT not found, using defaults"
    fi
    
    log_success "Prerequisites check passed"
}

# Build images
build_images() {
    log_info "Building Docker images..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE build
    else
        docker-compose build
    fi
    
    log_success "Docker images built successfully"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    # Start services for testing
    docker-compose up -d
    
    # Wait for services to be ready
    sleep 30
    
    # Run backend tests
    if docker-compose run --rm backend pytest tests/; then
        log_success "Backend tests passed"
    else
        log_error "Backend tests failed"
        stop_services
        exit 1
    fi
    
    # Run frontend tests
    if docker-compose run --rm frontend npm test; then
        log_success "Frontend tests passed"
    else
        log_error "Frontend tests failed"
        stop_services
        exit 1
    fi
    
    # Run integration tests
    if docker-compose run --rm backend pytest tests/test_integration.py; then
        log_success "Integration tests passed"
    else
        log_error "Integration tests failed"
        stop_services
        exit 1
    fi
    
    stop_services
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    docker-compose down
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    case $ENVIRONMENT in
        development)
            docker-compose up -d
            ;;
        staging)
            docker-compose -f $DOCKER_COMPOSE_FILE -f docker-compose.staging.yml up -d
            ;;
        production)
            docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE up -d
            ;;
    esac
    
    log_success "Services deployed successfully"
}

# Health check
health_check() {
    log_info "Performing health checks..."
    
    # Wait for services to start
    sleep 30
    
    # Run health check script
    if ./scripts/health-check.sh; then
        log_success "All services are healthy"
    else
        log_error "Health checks failed"
        exit 1
    fi
}

# Backup database (production only)
backup_database() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Backing up database..."
        
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="backup_${ENVIRONMENT}_${TIMESTAMP}.sql"
        
        if docker-compose exec -T database pg_dump -U demo_user demo_db > "$BACKUP_FILE"; then
            log_success "Database backed up to $BACKUP_FILE"
        else
            log_warning "Database backup failed"
        fi
    fi
}

# Main deployment function
deploy() {
    log_info "Starting deployment to $ENVIRONMENT environment"
    
    validate_environment
    check_prerequisites
    
    # For production, create backup first
    if [ "$ENVIRONMENT" = "production" ]; then
        backup_database
    fi
    
    # Build images
    build_images
    
    # Run tests (except in production where tests should run in CI)
    if [ "$ENVIRONMENT" != "production" ]; then
        run_tests
    fi
    
    # Deploy services
    deploy_services
    
    # Health check
    health_check
    
    log_success "Deployment to $ENVIRONMENT completed successfully!"
    
    # Display access information
    echo ""
    log_info "Access URLs:"
    echo "  Frontend:   http://localhost:8080"
    echo "  Jaeger UI:  http://localhost:16686"
    echo "  Zipkin UI:  http://localhost:9411"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana:    http://localhost:3000"
    echo ""
    
    # Show service status
    log_info "Service status:"
    docker-compose ps
}

# Rollback function
rollback() {
    log_info "Starting rollback..."
    
    # Stop current services
    stop_services
    
    # If we have a backup, restore it
    if [ -f "backup_${ENVIRONMENT}_*.sql" ]; then
        log_info "Restoring database from backup..."
        LATEST_BACKUP=$(ls -t backup_${ENVIRONMENT}_*.sql | head -1)
        docker-compose start database
        sleep 10
        docker-compose exec -T database psql -U demo_user demo_db < "$LATEST_BACKUP"
        log_success "Database restored from $LATEST_BACKUP"
    fi
    
    # Redeploy previous version (implementation depends on your setup)
    log_info "Redeploying previous version..."
    # Add your rollback logic here
    
    log_success "Rollback completed"
}

# Usage information
usage() {
    echo "Usage: $0 [environment] [action]"
    echo ""
    echo "Environments:"
    echo "  development (default)"
    echo "  staging"
    echo "  production"
    echo ""
    echo "Actions:"
    echo "  deploy (default)"
    echo "  rollback"
    echo "  health-check"
    echo ""
    echo "Examples:"
    echo "  $0                          # Deploy to development"
    echo "  $0 staging deploy           # Deploy to staging"
    echo "  $0 production rollback      # Rollback production"
    echo "  $0 health-check            # Run health checks"
}

# Parse arguments
ACTION=${2:-"deploy"}

case $ACTION in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    health-check)
        health_check
        ;;
    *)
        log_error "Invalid action: $ACTION"
        usage
        exit 1
        ;;
esac