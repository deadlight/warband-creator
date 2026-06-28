FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.7.1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

RUN poetry run python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "wargear.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
