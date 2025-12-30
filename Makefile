# -------------------------------------------------
# Variables
# -------------------------------------------------
APP_NAME=payment-gateway-simulator

# -------------------------------------------------
# Commands
# -------------------------------------------------
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make run            Run API locally"
	@echo "  make docker-up      Start services with Docker"
	@echo "  make docker-down    Stop Docker services"
	@echo "  make test           Run tests"
	@echo "  make format         Format code"
	@echo "  make lint           Lint code"

# -------------------------------------------------
# Local Development
# -------------------------------------------------
.PHONY: run
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# -------------------------------------------------
# Docker
# -------------------------------------------------
.PHONY: docker-up
docker-up:
	docker-compose up --build

.PHONY: docker-down
docker-down:
	docker-compose down

# -------------------------------------------------
# Testing
# -------------------------------------------------
.PHONY: test
test:
	pytest -v

# -------------------------------------------------
# Code Quality
# -------------------------------------------------
.PHONY: format
format:
	black app tests

.PHONY: lint
lint:
	ruff app tests
