FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

COPY . .
RUN poetry install --no-interaction --no-ansi

ENV PYTHONPATH=/app/src

CMD ["sh", "-c", "alembic upgrade head && python -m src.main"]
