#!/bin/bash

# Integrated ERP System Setup Script
# This script sets up the complete integrated ERP system

set -e

echo "🚀 Starting Integrated ERP System Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if required ports are available
check_ports() {
    print_status "Checking if required ports are available..."
    
    local ports=(80 3000 8000 5432 6379)
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port is already in use. Please free it up or modify the configuration."
        else
            print_success "Port $port is available"
        fi
    done
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/erpnext
    mkdir -p logs
    mkdir -p ssl
    
    print_success "Directories created"
}

# Set up environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# Database Configuration
POSTGRES_DB=erpnext
POSTGRES_USER=erpnext
POSTGRES_PASSWORD=erpnext123
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379

# ERPNext Configuration
FRAPPE_SITE=erpnext.local
FRAPPE_SITES_PATH=/home/frappe/frappe-bench/sites
SECRET_KEY=your-secret-key-here

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_ENV=development

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# AI/ML Configuration
AI_SERVICE_URL=http://ai-service:5000
ML_MODEL_PATH=/app/models
EOF
        print_success "Environment file created"
    else
        print_warning "Environment file already exists"
    fi
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    docker-compose build backend
    
    # Build frontend image
    print_status "Building frontend image..."
    docker-compose build frontend
    
    print_success "Docker images built successfully"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Start database and cache first
    print_status "Starting database and cache services..."
    docker-compose up -d db redis
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 30
    
    # Start backend
    print_status "Starting backend service..."
    docker-compose up -d backend
    
    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    sleep 60
    
    # Start frontend
    print_status "Starting frontend service..."
    docker-compose up -d frontend
    
    # Start nginx
    print_status "Starting nginx reverse proxy..."
    docker-compose up -d nginx
    
    print_success "All services started"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait for backend to be ready
    sleep 30
    
    # Run migrations
    docker-compose exec backend bench --site erpnext.local migrate
    
    print_success "Database migrations completed"
}

# Create initial data
create_initial_data() {
    print_status "Creating initial data..."
    
    # Create default users
    docker-compose exec backend bench --site erpnext.local execute erpnext.setup.utils.create_default_users
    
    # Create sample data
    docker-compose exec backend bench --site erpnext.local execute erpnext.setup.utils.create_sample_data
    
    print_success "Initial data created"
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Check backend health
    if curl -f http://localhost:8000/api/health >/dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend health
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend is healthy"
    else
        print_error "Frontend health check failed"
        return 1
    fi
    
    print_success "All services are healthy"
}

# Display access information
display_access_info() {
    print_success "🎉 Integrated ERP System setup completed successfully!"
    echo ""
    echo "📋 Access Information:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  Admin Panel: http://localhost:8000/app"
    echo ""
    echo "🔑 Default Credentials:"
    echo "  Username: Administrator"
    echo "  Password: admin123"
    echo ""
    echo "📊 Services Status:"
    docker-compose ps
    echo ""
    echo "📝 Useful Commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart services: docker-compose restart"
    echo "  Update system: docker-compose pull && docker-compose up -d"
}

# Main execution
main() {
    echo "🏢 Integrated ERP System Setup"
    echo "================================"
    echo ""
    
    check_docker
    check_ports
    create_directories
    setup_environment
    build_images
    start_services
    run_migrations
    create_initial_data
    health_check
    display_access_info
}

# Run main function
main "$@"
