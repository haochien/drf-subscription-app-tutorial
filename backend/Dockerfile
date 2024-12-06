# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# Install postgresql-client if you need CLI operations for postgresql db

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         postgresql-client \
#         libpq-dev \
#         gcc \
#         python3-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
# RUN pip install gunicorn

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy project
COPY . .

# # Create a non-root user
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser

# # Expose port
# EXPOSE 8000

# # Run gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]



# Create necessary directories
# RUN mkdir -p /app/logs /app/static /app/media

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]