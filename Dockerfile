# Use Python 3.9 slim bullseye for Raspberry Pi compatibility
FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies for Pi optimization
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    procps \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create assets directory for logos and trivia data
RUN mkdir -p /app/assets/logos /app/trivia/data

# Download and store all team logos during build
RUN python scripts/download_logos.py

# Create a non-root user for security
RUN useradd -m -u 1000 goobie && \
    chown -R goobie:goobie /app

# Switch to non-root user
USER goobie

# Set environment variables for Pi optimization
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check for Pi monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import psutil; exit(0 if psutil.virtual_memory().percent < 90 else 1)"

# Set the default command to run the bot
CMD ["python", "bot.py"]
