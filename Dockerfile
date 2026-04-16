# Build stage — install dependencies
FROM python:3.12-slim AS deps

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Production image
FROM python:3.12-slim

WORKDIR /app

# wizexercise.txt is required by the Wiz Technical Exercise spec.
# Copied here to prove the file exists in the running container image.
COPY wizexercise.txt ./wizexercise.txt

COPY --from=deps /install /usr/local
COPY app/ ./

EXPOSE 3000

USER nobody

CMD ["gunicorn", "app:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:3000", "--access-logfile", "-"]
