FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for python-ldap and mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/ requirements/

# Install Python dependencies (including mysqlclient for MySQL support)
RUN pip install --no-cache-dir -r requirements/requirements-base.txt \
    && pip install --no-cache-dir mysqlclient>=2.2.0

# Copy application code
COPY . .

# Create directories for database, static and media files
RUN mkdir -p /app/db /app/static /app/media

# Collect static files (ignore errors during build, will run again at startup)
RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Expose port
EXPOSE 8000

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "apps.ratticweb.wsgi:application"]
