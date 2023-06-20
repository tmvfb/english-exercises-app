# starting server
dev:
	python3.8 manage.py runserver

start:
	poetry run gunicorn task_manager.wsgi

# poetry commands for test
install:
	poetry build
	poetry install

# performing checks, formatting and lint
selfcheck:
	poetry check

sort:
	isort .

test:
	python3.8 manage.py test

lint:
	poetry run flake8 task_manager

check: sort selfcheck test lint

check-ci: selfcheck lint

# django-admin commands
shell:
	django-admin shell

trans:
	django-admin makemessages -l ru

compile:
	django-admin compilemessages

# test coverage reports
make test-coverage:
	poetry run coverage run --source='.' manage.py test task_manager
	poetry run coverage xml -o coverage.xml

.PHONY: dev start selfcheck test lint check trans compile sort test-coverage install
