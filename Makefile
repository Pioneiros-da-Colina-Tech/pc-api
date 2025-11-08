.PHONY: help install source deploy deploy-stg run dev migrate revision migrate-and-revision lint format check clean
REVISION_MSG := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

help:
	@echo "Available commands:"
	@echo "  install                        Install dependencies"
	@echo "  source                         Activate virtual environment"
	@echo "  run                            Run the application"
	@echo "  dev                            Run development server with uvicorn"
	@echo "  migrate                        Run database migrations"
	@echo "  revision                       Create a new database migration revision"
	@echo "  migrate-and-revision           Run full database migrations"
	@echo "  test                           Run tests with pytest"
	@echo "  lint                           Run linting with ruff"
	@echo "  format                         Format code with ruff"
	@echo "  check                          Run linting with fixes and format code"
	@echo "  clean                          Clean up temporary files"

install:
	uv sync

deploy:
	gcloud run deploy ng-sec-fidc-api --port 8000 --source . --project=ariz-function-prd --region us-central1

deploy-stg:
	gcloud run deploy ng-sec-fidc-api-stg --port 8000 --source . --project=ariz-function-prd --region us-central1

run:
	uv run python -m app.main

dev:
	uv run uvicorn --reload app.main:app --host 0.0.0.0

migrate:
	uv run alembic upgrade head

revision:
	uv run alembic revision --autogenerate -m "$(REVISION_MSG)"

migrate-and-revision:
	uv run alembic upgrade head && uv run alembic revision --autogenerate -m "$(REVISION_MSG)"

test:
	uv run pytest

lint:
	ruff check .

format:
	ruff format .

check:
	ruff check --extend-select=I,UP --fix . && ruff format .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
