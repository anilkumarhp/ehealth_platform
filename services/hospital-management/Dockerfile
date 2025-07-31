FROM python:3.12-slim

WORKDIR /app

# Copy and install requirements
COPY requirements/base.txt .
RUN pip install --no-cache-dir -r base.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=hms_config.settings.local

# Expose the port
EXPOSE 8005

# Run the application with auto-reload for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8005"]