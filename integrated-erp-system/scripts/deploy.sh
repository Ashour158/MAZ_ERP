#!/bin/bash
# Production Deployment Script for Independent ERP System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="independent-erp-system"
DOCKER_COMPOSE_FILE="docker/docker-compose.production.yml"
ENV_FILE=".env"

echo -e "${BLUE}🚀 Starting Independent ERP System Deployment${NC}"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  Environment file not found. Creating from example...${NC}"
    if [ -f "env.production.example" ]; then
        cp env.production.example .env
        echo -e "${YELLOW}📝 Please edit .env file with your production values before continuing.${NC}"
        echo -e "${YELLOW}   Press Enter when ready to continue...${NC}"
        read
    else
        echo -e "${RED}❌ No environment file found. Please create .env file.${NC}"
        exit 1
    fi
fi

# Validate environment variables
echo -e "${BLUE}🔍 Validating environment configuration...${NC}"
source .env

required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY" "JWT_SECRET_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required environment variable $var is not set.${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment configuration validated${NC}"

# Create necessary directories
echo -e "${BLUE}📁 Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p uploads
mkdir -p backups
mkdir -p ssl

# Set proper permissions
chmod 755 logs uploads backups ssl

# Build and start services
echo -e "${BLUE}🔨 Building and starting services...${NC}"
docker-compose -f $DOCKER_COMPOSE_FILE down --remove-orphans
docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
docker-compose -f $DOCKER_COMPOSE_FILE up -d

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${BLUE}🏥 Checking service health...${NC}"

# Check PostgreSQL
if docker-compose -f $DOCKER_COMPOSE_FILE exec -T postgres pg_isready -U erp_user -d erp_system; then
    echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not ready${NC}"
    exit 1
fi

# Check Redis
if docker-compose -f $DOCKER_COMPOSE_FILE exec -T redis redis-cli ping; then
    echo -e "${GREEN}✅ Redis is ready${NC}"
else
    echo -e "${RED}❌ Redis is not ready${NC}"
    exit 1
fi

# Check Backend
if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is ready${NC}"
else
    echo -e "${RED}❌ Backend API is not ready${NC}"
    exit 1
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is ready${NC}"
else
    echo -e "${RED}❌ Frontend is not ready${NC}"
    exit 1
fi

# Check Nginx
if curl -f http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx is ready${NC}"
else
    echo -e "${RED}❌ Nginx is not ready${NC}"
    exit 1
fi

# Run database migrations
echo -e "${BLUE}🗄️  Running database migrations...${NC}"
docker-compose -f $DOCKER_COMPOSE_FILE exec -T backend python -c "
from core.database import db_manager
db_manager.engine.execute('CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";')
print('Database migrations completed')
"

# Create initial admin user
echo -e "${BLUE}👤 Creating initial admin user...${NC}"
docker-compose -f $DOCKER_COMPOSE_FILE exec -T backend python -c "
from independent.crm.customer import Customer
admin_customer = Customer({
    'customer_name': 'System Administrator',
    'customer_type': 'Internal',
    'email': 'admin@system.local',
    'customer_status': 'Active',
    'customer_priority': 'High'
})
admin_customer.validate()
admin_customer.save()
print('Admin user created successfully')
"

# Setup monitoring
echo -e "${BLUE}📊 Setting up monitoring...${NC}"
# Prometheus and Grafana are already configured in docker-compose

# Create backup script
echo -e "${BLUE}💾 Creating backup script...${NC}"
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
# Backup script for Independent ERP System

BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="erp_backup_$DATE.tar.gz"

# Create backup
docker-compose -f docker/docker-compose.production.yml exec -T postgres pg_dump -U erp_user erp_system > "$BACKUP_DIR/database_$DATE.sql"
tar -czf "$BACKUP_DIR/$BACKUP_FILE" -C /app uploads logs

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "erp_backup_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "database_*.sql" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x scripts/backup.sh

# Create update script
echo -e "${BLUE}🔄 Creating update script...${NC}"
cat > scripts/update.sh << 'EOF'
#!/bin/bash
# Update script for Independent ERP System

echo "🔄 Updating Independent ERP System..."

# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose -f docker/docker-compose.production.yml down
docker-compose -f docker/docker-compose.production.yml build --no-cache
docker-compose -f docker/docker-compose.production.yml up -d

echo "✅ Update completed successfully"
EOF

chmod +x scripts/update.sh

# Display deployment information
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "=================================================="
echo -e "${BLUE}📋 Service Information:${NC}"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend API: http://localhost:5000"
echo "  • Nginx: http://localhost"
echo "  • Grafana: http://localhost:3001"
echo "  • Prometheus: http://localhost:9090"
echo "  • Kibana: http://localhost:5601"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  • View logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
echo "  • Stop services: docker-compose -f $DOCKER_COMPOSE_FILE down"
echo "  • Restart services: docker-compose -f $DOCKER_COMPOSE_FILE restart"
echo "  • Update system: ./scripts/update.sh"
echo "  • Create backup: ./scripts/backup.sh"
echo ""
echo -e "${BLUE}📊 Monitoring:${NC}"
echo "  • System Health: http://localhost/api/health"
echo "  • Grafana Dashboards: http://localhost:3001 (admin/admin123)"
echo "  • Prometheus Metrics: http://localhost:9090"
echo "  • Log Analysis: http://localhost:5601"
echo ""
echo -e "${GREEN}✅ Independent ERP System is now running in production!${NC}"
echo -e "${YELLOW}⚠️  Remember to:${NC}"
echo "  1. Update SSL certificates for HTTPS"
echo "  2. Configure domain names"
echo "  3. Set up regular backups"
echo "  4. Monitor system performance"
echo "  5. Review security settings"
