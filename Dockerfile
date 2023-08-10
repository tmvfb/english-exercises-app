FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY . /app/

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]