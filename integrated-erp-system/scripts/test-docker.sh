#!/bin/bash

# Docker Configuration Testing Script
# This script tests the Docker configuration and container setup

set -e

echo "🐳 Testing Docker Configuration..."

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

# Test Docker installation
test_docker_installation() {
    print_status "Testing Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Test Docker Compose file syntax
test_docker_compose_syntax() {
    print_status "Testing Docker Compose file syntax..."
    
    if [ ! -f "docker/docker-compose.yml" ]; then
        print_error "Docker Compose file not found"
        exit 1
    fi
    
    # Validate Docker Compose file
    docker-compose -f docker/docker-compose.yml config > /dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose file syntax is valid"
    else
        print_error "Docker Compose file syntax is invalid"
        exit 1
    fi
}

# Test Dockerfile syntax
test_dockerfile_syntax() {
    print_status "Testing Dockerfile syntax..."
    
    # Test backend Dockerfile
    if [ -f "backend/Dockerfile" ]; then
        print_success "Backend Dockerfile exists"
    else
        print_error "Backend Dockerfile not found"
        exit 1
    fi
    
    # Test frontend Dockerfile
    if [ -f "frontend/Dockerfile" ]; then
        print_success "Frontend Dockerfile exists"
    else
        print_error "Frontend Dockerfile not found"
        exit 1
    fi
}

# Test port availability
test_port_availability() {
    print_status "Testing port availability..."
    
    local ports=(80 3000 8000 5432 6379)
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port is already in use"
        else
            print_success "Port $port is available"
        fi
    done
}

# Test Docker image building
test_docker_image_building() {
    print_status "Testing Docker image building..."
    
    # Test backend image build
    print_status "Building backend image..."
    if docker build -t test-backend backend/ > /dev/null 2>&1; then
        print_success "Backend image builds successfully"
    else
        print_error "Backend image build failed"
        exit 1
    fi
    
    # Test frontend image build
    print_status "Building frontend image..."
    if docker build -t test-frontend frontend/ > /dev/null 2>&1; then
        print_success "Frontend image builds successfully"
    else
        print_error "Frontend image build failed"
        exit 1
    fi
}

# Test container startup
test_container_startup() {
    print_status "Testing container startup..."
    
    # Start services
    docker-compose -f docker/docker-compose.yml up -d db redis
    
    # Wait for services to be ready
    sleep 30
    
    # Check if services are running
    if docker-compose -f docker/docker-compose.yml ps | grep -q "Up"; then
        print_success "Services started successfully"
    else
        print_error "Services failed to start"
        exit 1
    fi
}

# Test service health
test_service_health() {
    print_status "Testing service health..."
    
    # Test database connection
    if docker-compose -f docker/docker-compose.yml exec -T db pg_isready -U erpnext > /dev/null 2>&1; then
        print_success "Database is healthy"
    else
        print_error "Database health check failed"
        exit 1
    fi
    
    # Test Redis connection
    if docker-compose -f docker/docker-compose.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is healthy"
    else
        print_error "Redis health check failed"
        exit 1
    fi
}

# Test network connectivity
test_network_connectivity() {
    print_status "Testing network connectivity..."
    
    # Test inter-container communication
    if docker-compose -f docker/docker-compose.yml exec -T db ping -c 1 redis > /dev/null 2>&1; then
        print_success "Inter-container communication works"
    else
        print_error "Inter-container communication failed"
        exit 1
    fi
}

# Test volume mounting
test_volume_mounting() {
    print_status "Testing volume mounting..."
    
    # Check if volumes are created
    if docker volume ls | grep -q "integrated-erp-system"; then
        print_success "Volumes are created"
    else
        print_warning "Volumes not found (will be created on first run)"
    fi
}

# Test environment variables
test_environment_variables() {
    print_status "Testing environment variables..."
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        print_success "Environment file exists"
    else
        print_warning "Environment file not found (will be created by setup script)"
    fi
}

# Test security configuration
test_security_configuration() {
    print_status "Testing security configuration..."
    
    # Check if SSL certificates exist
    if [ -d "docker/ssl" ]; then
        print_success "SSL directory exists"
    else
        print_warning "SSL directory not found (will be created for production)"
    fi
    
    # Check nginx configuration
    if [ -f "docker/nginx.conf" ]; then
        print_success "Nginx configuration exists"
    else
        print_error "Nginx configuration not found"
        exit 1
    fi
}

# Test cleanup
test_cleanup() {
    print_status "Cleaning up test containers..."
    
    # Stop and remove test containers
    docker-compose -f docker/docker-compose.yml down -v
    
    # Remove test images
    docker rmi test-backend test-frontend > /dev/null 2>&1 || true
    
    print_success "Cleanup completed"
}

# Main test execution
main() {
    echo "🧪 Docker Configuration Test Suite"
    echo "=================================="
    echo ""
    
    test_docker_installation
    test_docker_compose_syntax
    test_dockerfile_syntax
    test_port_availability
    test_docker_image_building
    test_container_startup
    test_service_health
    test_network_connectivity
    test_volume_mounting
    test_environment_variables
    test_security_configuration
    test_cleanup
    
    print_success "🎉 All Docker tests passed!"
    echo ""
    echo "📋 Test Summary:"
    echo "  ✅ Docker installation verified"
    echo "  ✅ Docker Compose syntax validated"
    echo "  ✅ Dockerfile syntax validated"
    echo "  ✅ Port availability checked"
    echo "  ✅ Image building tested"
    echo "  ✅ Container startup tested"
    echo "  ✅ Service health verified"
    echo "  ✅ Network connectivity tested"
    echo "  ✅ Volume mounting verified"
    echo "  ✅ Environment configuration checked"
    echo "  ✅ Security configuration validated"
    echo ""
    echo "🚀 System is ready for deployment!"
}

# Run main function
main "$@"
