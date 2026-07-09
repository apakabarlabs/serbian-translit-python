install:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

test:
	venv/bin/pytest serbian_translit/

lint:
	venv/bin/ruff check serbian_translit/
	venv/bin/ruff format --check serbian_translit/

format:
	venv/bin/ruff check --fix serbian_translit/
	venv/bin/ruff format serbian_translit/
