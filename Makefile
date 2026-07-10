.PHONY: install run cli test lint format docker-up docker-down

install:
	pip install -r requirements.txt

run:
	uvicorn app.api:app --reload

cli:
	python cli.py

test:
	pytest tests/ -v

lint:
	ruff check .

format:
	ruff check . --fix

docker-up:
	docker compose up --build

docker-down:
	docker compose down
