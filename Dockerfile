FROM python:3.12-slim

WORKDIR /app

# Install system dependencies

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Deno

ENV DENO_INSTALL=/usr/local

RUN curl -fsSL https://deno.land/install.sh | sh

ENV PATH="/usr/local/bin:${PATH}"

# Copy project files

COPY requirements.txt .

# Install Python dependencies

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start Flask application

CMD ["sh", "-c", "gunicorn --workers 1 --threads 4 --timeout 300 --bind 0.0.0.0:${PORT:-10000} app:app"]