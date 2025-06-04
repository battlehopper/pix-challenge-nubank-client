.PHONY: install lint test coverage

install:
	pip install -r requirements.txt

lint:
	ruff check .
	ruff format --check .
	mypy pix_client

test:
	pytest -q

coverage:
	pytest --cov=pix_client --cov-report=term-missing
