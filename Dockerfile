FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port required by Hugging Face
EXPOSE 7860

# Start the application
CMD ["sh", "-c", "cd mcp_server && python server.py & sleep 5 && cd ../backend && python -m uvicorn src.app:app --host 0.0.0.0 --port 7860"]