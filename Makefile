APP_NAME=ai-agent
IMAGE_DEV=$(APP_NAME):dev
IMAGE_PROD=$(APP_NAME):prod
PORT=8000

.PHONY: help venv dev run docker-dev docker-prod clean stop

help:
	@echo "Targets:"
	@echo "  venv        - create local venv and install deps"
	@echo "  dev         - run locally with uvicorn --reload"
	@echo "  docker-dev  - build + up dev container (hot reload)"
	@echo "  docker-prod - build + run prod container"
	@echo "  clean       - remove caches and containers"

venv:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

dev:
	. .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port $(PORT) --reload

run: dev

docker-dev:
	docker compose up --build -d
	docker compose logs -f

docker-prod:
	docker build --target prod -t $(IMAGE_PROD) .
	docker run -d --rm --name $(APP_NAME)-prod -p $(PORT):$(PORT) --env-file .env $(IMAGE_PROD)
	@echo ">>> Prod container started at http://localhost:$(PORT)"

clean:
	docker compose down
	docker rm -f $(APP_NAME)-prod || true
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache

stop:
	docker compose down
	-docker rm -f ai-agent-prod

