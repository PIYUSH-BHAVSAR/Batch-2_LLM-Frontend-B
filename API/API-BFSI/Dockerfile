FROM python:3.10-slim

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies (explicit additions included)
RUN pip install --no-cache-dir psycopg2 \
    && pip install --no-cache-dir "pydantic[email]" \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose port (Hugging Face uses 7860 by default)
EXPOSE 7860

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
