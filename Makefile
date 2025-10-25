.PHONY: help start stop clean test build deploy logs status setup

help:
	@echo "OpenTelemetry Demo - Available commands:"
	@echo "  setup   - Setup and start all services"
	@echo "  start   - Start all services with Docker Compose"
	@echo "  stop    - Stop all services"
	@echo "  clean   - Remove all containers and volumes"
	@echo "  test    - Run tests"
	@echo "  build   - Build all services"
	@echo "  deploy  - Deploy to production"
	@echo "  logs    - Show service logs"
	@echo "  status  - Show service status"

setup:
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

start:
	docker-compose up -d

stop:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -f

test:
	docker-compose run --rm backend pytest tests/
	docker-compose run --rm frontend npm test

build:
	docker-compose build

deploy:
	@echo "Deploying to production..."
	# Add your production deployment commands here

logs:
	docker-compose logs -f

status:
	docker-compose ps

health:
	@chmod +x scripts/health-check.sh
	@./scripts/health-check.sh

backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

collector-logs:
	docker-compose logs -f collector

restart:
	docker-compose restart