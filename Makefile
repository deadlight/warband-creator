.PHONY: help up down restart build logs shell db-shell migrate makemigrations \
        test test-cov format lint pre-commit install hooks clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with poetry
	poetry install

# ---- Docker ----

up: ## Start all containers
	docker compose up -d

down: ## Stop all containers
	docker compose down

restart: down up ## Restart all containers

build: ## Build docker images
	docker compose build

logs: ## Tail logs from all containers
	docker compose logs -f

shell: ## Open a shell inside the web container
	docker compose exec web bash

db-shell: ## Open a psql shell in the db container
	docker compose exec db psql -U wargear wargear

# ---- Django ----

migrate: ## Run django migrations
	docker compose exec web poetry run python manage.py migrate

makemigrations: ## Generate new migrations
	docker compose exec web poetry run python manage.py makemigrations

createsuperuser: ## Create a django superuser
	docker compose exec web poetry run python manage.py createsuperuser

# ---- Local Django (without containers) ----

run-local: ## Run django dev server locally
	poetry run python manage.py runserver

migrate-local: ## Run migrations locally
	poetry run python manage.py migrate

# ---- Code Quality ----

format: ## Format code with black
	poetry run black .

lint: ## Check formatting without changing files
	poetry run black --check .

pre-commit: ## Run pre-commit on all files
	poetry run pre-commit run --all-files

hooks: ## Install pre-commit hooks
	poetry run pre-commit install

# ---- Testing ----

test: ## Run tests
	poetry run pytest

test-cov: ## Run tests with coverage
	poetry run pytest --cov=wargear --cov-report=term-missing

test-docker: ## Run tests inside docker container
	docker compose exec web poetry run pytest

# ---- Cleanup ----

clean: ## Remove pycache and pytest cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
