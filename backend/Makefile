.PHONY: help migration upgrade downgrade restart test build-morphology clear-db logs logs-follow clean

help:
	@echo "Available commands:"
	@echo "  make migration MSG='message'  - Create a new alembic migration"
	@echo "  make upgrade                  - Run alembic upgrade to head"
	@echo "  make downgrade                - Downgrade alembic by 1 revision"
	@echo "  make restart                  - Restart backend container"
	@echo "  make test                     - Run pytest tests"
	@echo "  make build-morphology         - Run morphology database builder"
	@echo "  make clear-db                 - Clear all data from database tables"
	@echo "  make logs                     - Show backend container logs (last 20)"
	@echo "  make logs-live              - Follow backend container logs (live)"
	@echo "  make clean                    - Clean up __pycache__ and .pyc files"

migration:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide a migration message. Usage: make migration MSG='your message'"; \
		exit 1; \
	fi
	docker exec quran_app_backend alembic revision --autogenerate -m "$(MSG)"

upgrade:
	docker exec quran_app_backend alembic upgrade head

downgrade:
	docker exec quran_app_backend alembic downgrade -1

restart:
	docker restart quran_app_backend

test:
	docker exec quran_app_backend pytest

build-morphology:
	@curl -X POST "http://localhost:8000/api/admin/build-morphology"
	@echo ""

clear-db:
	@curl -X DELETE "http://localhost:8000/api/admin/clear-database?confirm=YES_DELETE_ALL"
	@echo ""

logs:
	docker logs --tail 20 quran_app_backend

logs-live:
	docker logs -f quran_app_backend

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
