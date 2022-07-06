PACKAGE = nvmodel-0.1.0

.PHONY: build
build:
	poetry build
	tar zxvf dist/$(PACKAGE).tar.gz -C ./dist
	cp dist/$(PACKAGE)/setup.py setup.py
	rm -rf dist

.PHONY: format
format:
	poetry run isort . && poetry run black .

.PHONY: test
test:
	poetry run python -m pytest

.PHONY: lint
lint:
	poetry run flake8