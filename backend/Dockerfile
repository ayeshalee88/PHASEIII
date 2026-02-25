# Backend Dockerfile - FastAPI with PostgreSQL
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for asyncpg and psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the backend port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
