.DEFAULT_GOAL := build

.PHONY: install install-tools build test docs comments lint format wheel-smoke clean

COMMENTCENSOR_VERSION ?= v0.3.2
COMMENTCENSOR_ENV = .tools/commentcensor
COMMENTCENSOR = $(COMMENTCENSOR_ENV)/bin/commentcensor

install:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip setuptools
	venv/bin/pip install -e ".[dev]"

install-tools:
	python3 -m venv $(COMMENTCENSOR_ENV)
	$(COMMENTCENSOR_ENV)/bin/pip install --quiet --upgrade git+https://github.com/botforge-pro/commentcensor.git@$(COMMENTCENSOR_VERSION)

test:
	venv/bin/pytest --cov --cov-report=term-missing

docs:
	venv/bin/pdoc serbian_translit -o build/docs

comments:
	$(COMMENTCENSOR) .

lint: comments
	venv/bin/ruff check serbian_translit tests
	venv/bin/ruff format --check serbian_translit tests
	venv/bin/mypy serbian_translit tests

format:
	venv/bin/ruff check --fix serbian_translit tests
	venv/bin/ruff format serbian_translit tests

build: lint test docs
	venv/bin/python -m build
	venv/bin/python -m twine check dist/*

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache

wheel-smoke:
	rm -rf build dist
	venv/bin/python -m build --wheel --no-isolation
	rm -rf /tmp/serbian-translit-smoke
	python3 -m venv /tmp/serbian-translit-smoke
	/tmp/serbian-translit-smoke/bin/pip install dist/*.whl
	/tmp/serbian-translit-smoke/bin/python -c "\
import serbian_translit; \
from serbian_translit import srp, cnr; \
assert serbian_translit.__version__; \
assert srp.to_cyr('Beograd') == 'Београд'; \
assert srp.to_lat('Њујорк') == 'Njujork'; \
assert cnr.to_cyr('śever') == 'с́евер'; \
assert cnr.to_lat('с́евер') == 'śever'; \
print('OK version=' + serbian_translit.__version__)"
	rm -rf /tmp/serbian-translit-smoke
