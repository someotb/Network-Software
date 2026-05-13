.PHONY: help build up down logs clean test

help:
	@echo "Tickets System - Makefile commands"
	@echo ""
	@echo "  make build    - Build all Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - Show logs"
	@echo "  make clean    - Stop and remove all containers, volumes"
	@echo "  make test     - Run tests"
	@echo "  make restart  - Restart all services"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Waiting for services to start..."
	@sleep 10
	@echo "Services started!"
	@echo "API Gateway: http://localhost"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all

test:
	pytest tests/ -v

restart: down up

status:
	docker-compose ps

health:
	@echo "Checking service health..."
	@curl -s http://localhost/health || echo "Gateway not responding"
	@curl -s http://localhost:8124/health || echo "Tickets service not responding"
	@curl -s http://localhost:8125/health || echo "Users service not responding"
	@curl -s http://localhost:8126/health || echo "Analytics service not responding"
