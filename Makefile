IMAGE_NAME = books-scraper
CONTAINER_NAME = books-scraper
DATA_DIR = ./data

# Build the Docker image
.PHONY: build
build:
	@echo "Building Docker image..."
	docker-compose build

# Run the scraper only
.PHONY: scrape
scrape:
	@echo "Running books scraper..."
	@mkdir -p $(DATA_DIR)
	docker-compose up books-scraper --remove-orphans

# Run the API only
.PHONY: api
api:
	@echo "Starting Books API..."
	@mkdir -p $(DATA_DIR)
	docker-compose up books-api --remove-orphans

# Run both scraper and API
.PHONY: dev
dev:
	@echo "Starting development environment (scraper + API)..."
	@mkdir -p $(DATA_DIR)
	docker-compose up --remove-orphans

# Build and run scraper
.PHONY: build-scrape
build-scrape: build scrape

# Build and run API
.PHONY: build-api
build-api: build api

# Build and run development environment
.PHONY: build-dev
build-dev: build dev

# Show logs for scraper
.PHONY: logs-scraper
logs-scraper:
	docker-compose logs -f books-scraper

# Show logs for API
.PHONY: logs-api
logs-api:
	docker-compose logs -f books-api

# Show all logs
.PHONY: logs
logs:
	docker-compose logs -f

# Clean up containers and images
.PHONY: clean
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

# Clean scraped data
.PHONY: data-clean
data-clean:
	@echo "Cleaning scraped data..."
	rm -rf $(DATA_DIR)/*
	@echo "Data directory cleaned."

# Stop running containers
.PHONY: stop
stop:
	@echo "Stopping containers..."
	docker-compose down

# Install dependencies locally with Poetry
.PHONY: install
install:
	@echo "Installing dependencies with Poetry..."
	poetry install

# Run scraper locally (development)
.PHONY: local-scrape
local-scrape:
	@echo "Running scraper locally..."
	@mkdir -p $(DATA_DIR)
	poetry run python -m module_1.script.books_scraping

# Run API locally (development)
.PHONY: local-api
local-api:
	@echo "Starting API locally..."
	@mkdir -p $(DATA_DIR)
	poetry run uvicorn module_1.api.main:app --host 0.0.0.0 --port 8000 --reload

# Show help
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  build          - Build Docker images"
	@echo "  scrape         - Run only the scraper"
	@echo "  api            - Run only the API"
	@echo "  dev            - Run both scraper and API"
	@echo "  build-scrape   - Build and run scraper"
	@echo "  build-api      - Build and run API"
	@echo "  build-dev      - Build and run development environment"
	@echo "  install        - Install dependencies locally with Poetry"
	@echo "  local-scrape   - Run scraper locally (development)"
	@echo "  local-api      - Run API locally (development)"
	@echo "  logs           - Show all logs"
	@echo "  logs-scraper   - Show scraper logs"
	@echo "  logs-api       - Show API logs"
	@echo "  clean          - Clean up Docker resources"
	@echo "  data-clean     - Clean scraped data"
	@echo "  stop           - Stop containers"
	@echo "  help           - Show this help"
