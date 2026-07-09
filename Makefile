install:
	python3 -m venv venv
	venv/bin/pip install -e ".[dev]" pytest pytest-cov ruff mypy types-PyYAML build

test:
	venv/bin/pytest --cov

lint:
	venv/bin/ruff check serbian_translit
	venv/bin/ruff format --check serbian_translit
	venv/bin/mypy serbian_translit

format:
	venv/bin/ruff check --fix serbian_translit
	venv/bin/ruff format serbian_translit

wheel-smoke:
	rm -rf dist
	venv/bin/python -m build --wheel
	python3 -m venv /tmp/serbian-translit-smoke
	/tmp/serbian-translit-smoke/bin/pip install dist/*.whl
	/tmp/serbian-translit-smoke/bin/python -c "from serbian_translit import srp; assert srp.to_cyr('Beograd') == 'Београд'; print('OK')"
	rm -rf /tmp/serbian-translit-smoke
