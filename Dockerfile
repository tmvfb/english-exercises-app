FROM python:3.9-slim
ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY . /app/

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
RUN python3 manage.py collectstatic --noinput

EXPOSE 8000
CMD python3 manage.py migrate && gunicorn english_exercises_app.wsgi --timeout 300