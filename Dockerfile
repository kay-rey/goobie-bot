# Use Python 3.9 slim bullseye for Raspberry Pi compatibility
FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create assets directory for logos
RUN mkdir -p /app/assets/logos

# Download and store all team logos during build
RUN python scripts/download_logos.py

# Set the default command to run the bot
CMD ["python", "bot.py"]
