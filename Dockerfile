# ==============================================================================
# Use the official Python base image
FROM python:3.9 AS builder

# Set the working directory inside the container
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc curl cron \
    && apt-get clean

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN python -m pip install -U pip
RUN pip wheel --no-cache-dir \
    --no-deps \
    --wheel-dir /code/wheels \
    -r requirements.txt

FROM python:3.9-slim AS runtime

WORKDIR /code

COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .

# Copy the application code to the working directory
COPY app/ ./app
COPY main.py .

RUN mkdir artifact/

RUN python -m pip install -U pip
RUN pip install --no-cache /wheels/*

EXPOSE 8000

ENTRYPOINT uvicorn main:app --port 8000 --host 0.0.0.0
