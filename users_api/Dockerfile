FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false

COPY . .

RUN poetry install --no-interaction --no-ansi

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run python -m src.main"]
