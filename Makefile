APP_NAME=ai-agent
IMAGE_DEV=$(APP_NAME):dev
IMAGE_PROD=$(APP_NAME):prod
PORT=8000
CONTAINER_PORT=8080

.PHONY: help venv dev run docker-dev docker-prod clean stop fmt lint

help:
	@echo "Targets:"
	@echo "  venv        - create local venv and install deps (runtime + dev)"
	@echo "  dev         - run locally with uvicorn --reload (dotenv handled in app)"
	@echo "  docker-dev  - build + up dev container (hot reload)"
	@echo "  docker-prod - build + run prod container"
	@echo "  fmt         - black format"
	@echo "  lint        - ruff lint"
	@echo "  clean       - remove caches and containers"
	@echo "  stop        - docker compose down"

venv:
	python3 -m venv .venv
	. .venv/bin/activate && \
	  pip install --upgrade pip setuptools wheel && \
	  pip install -r requirements.txt -r requirements-dev.txt

dev:
	# .env is loaded by python-dotenv in app.main
	. .venv/bin/activate && \
	uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --reload

run: dev

docker-dev:
	docker compose up --build -d
	docker compose logs -f

docker-prod:
	# Build a lean prod image from the same Dockerfile
	docker build -t $(IMAGE_PROD) .
	docker run -d --rm --name $(APP_NAME)-prod \
	  -p $(PORT):$(CONTAINER_PORT) \
	  --env-file .env \
	  $(IMAGE_PROD)
	@echo ">>> Prod container started at http://localhost:$(PORT)"

fmt:
	. .venv/bin/activate && black app

lint:
	. .venv/bin/activate && ruff check app

clean:
	docker compose down
	docker rm -f $(APP_NAME)-prod 2>/dev/null || true
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache .venv

stop:
	docker compose down
