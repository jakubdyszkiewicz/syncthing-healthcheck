FROM python:3.11-alpine

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY healthcheck.py .

# Create config directory
RUN mkdir -p /config

# Set environment variable for config path
ENV CONFIG_PATH=/config/config.yaml

# Run the healthcheck service
CMD ["python", "-u", "healthcheck.py"]
