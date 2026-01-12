.PHONY: help back front dev up down logs migrate migrate-create test clean build-prod push-prod deploy-prod

help:
	@echo "Available commands:"
	@echo "  make back          - Run backend server"
	@echo "  make front         - Run frontend dev server"
	@echo "  make dev           - Run both backend and frontend"
	@echo "  make up            - Start Docker services (PostgreSQL + Qdrant)"
	@echo "  make down          - Stop Docker services"
	@echo "  make logs          - View Docker logs"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migrate-create MSG='description' - Create new migration"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean up cache and temp files"
	@echo ""
	@echo "Production commands:"
	@echo "  make build-prod    - Build production Docker images"
	@echo "  make push-prod     - Push images to DockerHub"
	@echo "  make deploy-prod   - Deploy with docker-compose"

back:
	PYTHONPATH=. .venv/bin/python3 -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

front:
	cd front && npm run dev

dev:
	@echo "Starting development environment..."
	@make -j2 back front

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	PYTHONPATH=. .venv/bin/alembic upgrade head

migrate-create:
	PYTHONPATH=. .venv/bin/alembic revision --autogenerate -m "$(MSG)"

test:
	PYTHONPATH=. .venv/bin/python3 scripts/test_api.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/

# Production commands
build-prod:
	@echo "🔨 Building production images..."
	@./deploy/build.sh

push-prod:
	@echo "🚀 Pushing to DockerHub..."
	@./deploy/push.sh

deploy-prod:
	@echo "🚀 Deploying production stack..."
	docker-compose -f deploy/docker-compose.prod.yml up -d
	@echo "✅ Deployment complete!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
