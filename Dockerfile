
FROM python:3.12-slim

WORKDIR /app

# Copy Deno binary from official Deno image
COPY --from=denoland/deno:bin-2.9.7 /deno /usr/local/bin/deno

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set environment
ENV PATH="/usr/local/bin:${PATH}"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Start server
CMD ["sh", "-c", "gunicorn --workers 1 --threads 4 --timeout 300 --bind 0.0.0.0:${PORT:-10000} app:app"]
