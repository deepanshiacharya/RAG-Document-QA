FROM python:3.12-slim

WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Set PYTHONPATH
ENV PYTHONPATH=/app
