export PYTHONPATH=src

lint:
	uvx ruff format
	uvx ruff check --fix

run:
	uv run python src/timeline/main.py DIG-23224

build:
	uv build

clean:
	rm -rf dist
	rm -rf build
	rm -rf src/timeline.egg-info
