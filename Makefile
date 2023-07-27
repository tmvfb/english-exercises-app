# starting server
dev:
	python3 manage.py runserver

start:
	poetry run gunicorn english_exercises_app.wsgi --timeout 300

# poetry commands for test
github-install:
	poetry build
	poetry install

install:
	poetry build
	poetry install
	poetry shell

# performing checks, formatting and lint
selfcheck:
	poetry check

sort:
	isort .

test:
	python3 manage.py test

lint:
	poetry run flake8 english_exercises_app

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
