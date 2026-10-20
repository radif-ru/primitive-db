.PHONY: install run build check-build package-install lint format test

install:
	uv sync

run:
	uv run database

build:
	uv build

check-build: build
	uvx twine@7.0.0 check dist/*

package-install: build
	uv tool install --force dist/*.whl

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run python -m doctest src/primitive_db/*.py
