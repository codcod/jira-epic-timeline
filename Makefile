export PYTHONPATH=src

lint:
	uvx ruff format
	uvx ruff check --fix

test:
	uv run pytest

test-verbose:
	uv run pytest -v

test-coverage:
	uv run pytest --cov=timeline --cov-report=term-missing

run:
	uv run python src/timeline/main.py DIG-23224

build:
	uv build

clean:
	rm -rf dist
	rm -rf build
	rm -rf src/timeline.egg-info
