export PYTHONPATH=src

lint:
	uvx ruff format
	uvx ruff check --fix

run:
	./bin/tl DIG-23224

build:
	uv build

clean:
	rm -rf dist
	rm -rf build
	rm -rf src/timeline.egg-info
