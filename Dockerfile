FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY levistock/ levistock/
COPY run_scheduler.py .

RUN pip install --no-cache-dir -e .

CMD ["python", "run_scheduler.py"]
