.PHONY: help setup-low setup-mid setup-high setup ingest eval clean test lint

help:
	@echo "SAHAYAK-AI Makefile"
	@echo "==================="
	@echo ""
	@echo "Available targets:"
	@echo "  setup-low      - Setup for low-end hardware (CPU-only, Gemma-2 2B)"
	@echo "  setup-mid     - Setup for mid-range hardware (16GB RAM, LLaMA-3 8B)"
	@echo "  setup-high    - Setup for high-end hardware (32GB+ RAM + GPU)"
	@echo "  ingest        - Ingest NDMA documents into ChromaDB"
	@echo "  eval          - Run evaluation benchmark"
	@echo "  test          - Run unit tests"
	@echo "  lint          - Run code linting"
	@echo "  clean         - Clean generated files and containers"

setup-low:
	@echo "Setting up SAHAYAK-AI for low-end hardware..."
	@bash scripts/setup/pull_models.sh low
	@bash scripts/setup/download_osm.sh
	@bash scripts/setup/convert_tiles.sh
	@python scripts/setup/ingest_ndma_docs.py
	@docker-compose -f docker-compose.low.yml up -d
	@echo "SAHAYAK-AI (Low-End) is running at http://localhost:3000"

setup-mid:
	@echo "Setting up SAHAYAK-AI for mid-range hardware..."
	@bash scripts/setup/pull_models.sh mid
	@bash scripts/setup/download_osm.sh
	@bash scripts/setup/convert_tiles.sh
	@python scripts/setup/ingest_ndma_docs.py
	@docker-compose -f docker-compose.mid.yml up -d
	@echo "SAHAYAK-AI (Mid-Range) is running at http://localhost:3000"

setup-high:
	@echo "Setting up SAHAYAK-AI for high-end hardware..."
	@bash scripts/setup/pull_models.sh high
	@bash scripts/setup/download_osm.sh
	@bash scripts/setup/convert_tiles.sh
	@python scripts/setup/ingest_ndma_docs.py
	@docker-compose -f docker-compose.high.yml up -d
	@echo "SAHAYAK-AI (High-End) is running at http://localhost:3000"

ingest:
	@python scripts/setup/ingest_ndma_docs.py

eval:
	@python scripts/eval/benchmark.py

test:
	@python -m pytest tests/ -v --cov=backend --cov-report=html

lint:
	@python -m ruff check backend/
	@python -m mypy backend/

clean:
	@docker-compose -f docker-compose.low.yml down -v 2>/dev/null || true
	@docker-compose -f docker-compose.mid.yml down -v 2>/dev/null || true
	@docker-compose -f docker-compose.high.yml down -v 2>/dev/null || true
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf data/chroma_db/*
	@rm -rf data/poi/poi.duckdb
	@echo "Cleaned up containers and generated files"