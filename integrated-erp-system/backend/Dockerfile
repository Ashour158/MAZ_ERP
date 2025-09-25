# Backend Dockerfile for Integrated ERP System
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libffi-dev \
    libssl-dev \
    libmariadb-dev \
    pkg-config \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for frontend assets
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install ERPNext
RUN bench init frappe-bench --frappe-branch version-14 --python python3 \
    && cd frappe-bench \
    && bench get-app erpnext --branch version-14 \
    && bench get-app maintenance \
    && bench get-app supply_chain \
    && bench get-app enhanced_crm \
    && bench get-app ai_analytics

# Create new site
RUN cd frappe-bench \
    && bench new-site erpnext.local --mariadb-root-password erpnext123 --admin-password admin123

# Install apps
RUN cd frappe-bench \
    && bench --site erpnext.local install-app erpnext \
    && bench --site erpnext.local install-app maintenance \
    && bench --site erpnext.local install-app supply_chain \
    && bench --site erpnext.local install-app enhanced_crm \
    && bench --site erpnext.local install-app ai_analytics

# Set up supervisor for process management
RUN apt-get update && apt-get install -y supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy supervisor configuration
COPY docker/supervisor.conf /etc/supervisor/conf.d/erpnext.conf

# Create necessary directories
RUN mkdir -p /var/log/supervisor \
    && mkdir -p /home/frappe/frappe-bench/sites \
    && chown -R frappe:frappe /home/frappe

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
