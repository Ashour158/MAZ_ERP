#!/bin/bash
# DigitalOcean Deployment Script for Independent ERP System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 DigitalOcean Deployment for Independent ERP System${NC}"
echo "=================================================="

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo -e "${RED}❌ This script is designed for Ubuntu/Debian systems.${NC}"
    echo -e "${YELLOW}For other systems, please follow the manual deployment guide.${NC}"
    exit 1
fi

# Update system
echo -e "${BLUE}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install required packages
echo -e "${BLUE}📦 Installing required packages...${NC}"
apt install -y curl wget git nano htop ufw fail2ban

# Install Docker
echo -e "${BLUE}🐳 Installing Docker...${NC}"
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Add user to docker group
usermod -aG docker $USER

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Install Docker Compose
echo -e "${BLUE}🐳 Installing Docker Compose...${NC}"
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installations
echo -e "${BLUE}✅ Verifying installations...${NC}"
docker --version
docker-compose --version

# Create application directory
echo -e "${BLUE}📁 Creating application directory...${NC}"
mkdir -p /opt/erp-system
cd /opt/erp-system

# Check if repository is already cloned
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📥 Please clone your repository or upload files to /opt/erp-system${NC}"
    echo -e "${YELLOW}   You can use: git clone <your-repo-url> .${NC}"
    echo -e "${YELLOW}   Or upload files using SCP: scp -r /path/to/integrated-erp-system root@$(hostname -I | awk '{print $1}'):/opt/erp-system/${NC}"
    echo -e "${YELLOW}   Press Enter when ready to continue...${NC}"
    read
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Environment file not found. Creating from example...${NC}"
    if [ -f "env.production.example" ]; then
        cp env.production.example .env
        echo -e "${YELLOW}📝 Please edit .env file with your production values:${NC}"
        echo -e "${YELLOW}   nano .env${NC}"
        echo -e "${YELLOW}   Press Enter when ready to continue...${NC}"
        read
    else
        echo -e "${RED}❌ No environment file found. Please create .env file.${NC}"
        exit 1
    fi
fi

# Configure firewall
echo -e "${BLUE}🔥 Configuring firewall...${NC}"
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Configure fail2ban
echo -e "${BLUE}🛡️  Configuring fail2ban...${NC}"
systemctl enable fail2ban
systemctl start fail2ban

# Create necessary directories
echo -e "${BLUE}📁 Creating necessary directories...${NC}"
mkdir -p logs uploads backups ssl

# Set proper permissions
chmod 755 logs uploads backups ssl

# Build and start services
echo -e "${BLUE}🔨 Building and starting services...${NC}"
docker-compose -f docker/docker-compose.production.yml down --remove-orphans
docker-compose -f docker/docker-compose.production.yml build --no-cache
docker-compose -f docker/docker-compose.production.yml up -d

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${BLUE}🏥 Checking service health...${NC}"

# Check PostgreSQL
if docker-compose -f docker/docker-compose.production.yml exec -T postgres pg_isready -U erp_user -d erp_system; then
    echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not ready${NC}"
    exit 1
fi

# Check Redis
if docker-compose -f docker/docker-compose.production.yml exec -T redis redis-cli ping; then
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
docker-compose -f docker/docker-compose.production.yml exec -T backend python -c "
from core.database import db_manager
try:
    db_manager.engine.execute('CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";')
    print('Database migrations completed')
except Exception as e:
    print(f'Database migration error: {e}')
"

# Create initial admin user
echo -e "${BLUE}👤 Creating initial admin user...${NC}"
docker-compose -f docker/docker-compose.production.yml exec -T backend python -c "
from independent.crm.customer import Customer
try:
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
except Exception as e:
    print(f'Admin user creation error: {e}')
"

# Setup SSL (optional)
echo -e "${BLUE}🔒 SSL Setup (Optional)${NC}"
echo -e "${YELLOW}To setup SSL certificates:${NC}"
echo -e "${YELLOW}1. Install certbot: apt install certbot python3-certbot-nginx -y${NC}"
echo -e "${YELLOW}2. Stop nginx: docker-compose -f docker/docker-compose.production.yml stop nginx${NC}"
echo -e "${YELLOW}3. Get certificate: certbot certonly --standalone -d yourdomain.com${NC}"
echo -e "${YELLOW}4. Update nginx config with SSL paths${NC}"
echo -e "${YELLOW}5. Restart nginx: docker-compose -f docker/docker-compose.production.yml start nginx${NC}"

# Create management scripts
echo -e "${BLUE}📝 Creating management scripts...${NC}"

# Create backup script
cat > /opt/erp-system/scripts/backup.sh << 'EOF'
#!/bin/bash
# Backup script for Independent ERP System

BACKUP_DIR="/opt/erp-system/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="erp_backup_$DATE.tar.gz"

# Create backup
docker-compose -f docker/docker-compose.production.yml exec -T postgres pg_dump -U erp_user erp_system > "$BACKUP_DIR/database_$DATE.sql"
tar -czf "$BACKUP_DIR/$BACKUP_FILE" -C /opt/erp-system uploads logs

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "erp_backup_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "database_*.sql" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x /opt/erp-system/scripts/backup.sh

# Create update script
cat > /opt/erp-system/scripts/update.sh << 'EOF'
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

chmod +x /opt/erp-system/scripts/update.sh

# Create health check script
cat > /opt/erp-system/scripts/health-check.sh << 'EOF'
#!/bin/bash
# Health check script for Independent ERP System

echo "🏥 Checking system health..."

# Check services
services=("postgres" "redis" "backend" "frontend" "nginx")
for service in "${services[@]}"; do
    if docker-compose -f docker/docker-compose.production.yml ps $service | grep -q "Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not running"
    fi
done

# Check API health
if curl -f http://localhost/api/health > /dev/null 2>&1; then
    echo "✅ API is responding"
else
    echo "❌ API is not responding"
fi

echo "Health check completed"
EOF

chmod +x /opt/erp-system/scripts/health-check.sh

# Setup cron jobs
echo -e "${BLUE}⏰ Setting up cron jobs...${NC}"
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/erp-system/scripts/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/erp-system/scripts/health-check.sh") | crontab -

# Display deployment information
echo ""
echo -e "${GREEN}🎉 DigitalOcean Deployment completed successfully!${NC}"
echo "=================================================="
echo -e "${BLUE}📋 Service Information:${NC}"
echo "  • Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo "  • Backend API: http://$(hostname -I | awk '{print $1}'):5000"
echo "  • Nginx: http://$(hostname -I | awk '{print $1}')"
echo "  • Grafana: http://$(hostname -I | awk '{print $1}'):3001"
echo "  • Prometheus: http://$(hostname -I | awk '{print $1}'):9090"
echo "  • Kibana: http://$(hostname -I | awk '{print $1}'):5601"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  • View logs: docker-compose -f docker/docker-compose.production.yml logs -f"
echo "  • Stop services: docker-compose -f docker/docker-compose.production.yml down"
echo "  • Restart services: docker-compose -f docker/docker-compose.production.yml restart"
echo "  • Update system: /opt/erp-system/scripts/update.sh"
echo "  • Create backup: /opt/erp-system/scripts/backup.sh"
echo "  • Health check: /opt/erp-system/scripts/health-check.sh"
echo ""
echo -e "${BLUE}📊 Monitoring:${NC}"
echo "  • System Health: http://$(hostname -I | awk '{print $1}')/api/health"
echo "  • Grafana Dashboards: http://$(hostname -I | awk '{print $1}'):3001 (admin/admin123)"
echo "  • Prometheus Metrics: http://$(hostname -I | awk '{print $1}'):9090"
echo "  • Log Analysis: http://$(hostname -I | awk '{print $1}'):5601"
echo ""
echo -e "${GREEN}✅ Independent ERP System is now running on DigitalOcean!${NC}"
echo -e "${YELLOW}⚠️  Next steps:${NC}"
echo "  1. Point your domain to this server's IP: $(hostname -I | awk '{print $1}')"
echo "  2. Setup SSL certificates for HTTPS"
echo "  3. Configure monitoring alerts"
echo "  4. Test all functionality"
echo "  5. Setup regular backups"
echo ""
echo -e "${BLUE}🔗 Access your ERP system at: http://$(hostname -I | awk '{print $1}')${NC}"
