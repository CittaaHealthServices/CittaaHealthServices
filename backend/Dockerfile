# Use Python 3.12 to ensure psycopg2-binary compatibility
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 and audio processing
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Set environment variable for port
ENV PORT=8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
