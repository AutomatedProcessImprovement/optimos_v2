.PHONY: test coverage clean docker-build docker-up docker-down docker-build-local docker-up-local docker-down-local lint lint-fix format typecheck

# Make the 'docker-up' target the default when just running 'make'
.DEFAULT_GOAL := docker-up-local

test:
	python -m pytest

coverage:
	python -m pytest --cov=o2 --cov-report=term-missing

cov_out/index.html: coverage
	python -m pytest --cov=o2 --cov-report=term-missing --cov-report=html:cov_out

coverage-html: cov_out/index.html

coverage.xml: coverage
	python -m pytest --cov=o2 --cov-report=term-missing --cov-report=xml

coverage-xml: coverage.xml

coverage-full: coverage-html coverage-xml
	@echo "All coverage reports generated"

# Code quality targets
lint:
	python -m ruff check o2 o2_server

lint-fix:
	python -m ruff check --fix o2 o2_server

format:
	python -m ruff format o2 o2_server

typecheck:
	python -m pyright o2 o2_server


# Docker production targets
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Docker local development targets
docker-build-local:
	docker-compose -f docker-compose.local.yaml build

docker-up-local:
	docker-compose -f docker-compose.local.yaml up -d

docker-down-local:
	docker-compose -f docker-compose.local.yaml down

clean:
	rm -rf cov_out coverage.xml .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} + 