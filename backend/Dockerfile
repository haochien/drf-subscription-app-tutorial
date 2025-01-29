# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy project
COPY . .

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]