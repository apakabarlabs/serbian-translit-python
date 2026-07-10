install:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -e ".[dev]"

test:
	venv/bin/pytest --cov --cov-report=term-missing

lint:
	venv/bin/ruff check serbian_translit tests
	venv/bin/ruff format --check serbian_translit tests
	venv/bin/mypy serbian_translit tests

format:
	venv/bin/ruff check --fix serbian_translit tests
	venv/bin/ruff format serbian_translit tests

wheel-smoke:
	rm -rf dist
	venv/bin/python -m build --wheel
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
