# 🚀 **DIGITALOCEAN DEPLOYMENT GUIDE**

## 📋 **COMPLETE DEPLOYMENT STEPS FOR DIGITALOCEAN**

This guide will walk you through deploying the Independent ERP System on DigitalOcean using Droplets and Docker.

---

## 🎯 **DEPLOYMENT OPTIONS**

### **✅ OPTION 1: DROPLET DEPLOYMENT (RECOMMENDED)**
- **Cost**: $20-40/month
- **Setup**: 30-45 minutes
- **Scalability**: Manual scaling
- **Best for**: Small to medium businesses

### **✅ OPTION 2: KUBERNETES DEPLOYMENT**
- **Cost**: $50-100/month
- **Setup**: 60-90 minutes
- **Scalability**: Auto-scaling
- **Best for**: Large businesses, high availability

---

## 🚀 **OPTION 1: DROPLET DEPLOYMENT**

### **STEP 1: CREATE DIGITALOCEAN DROPLET**

#### **1.1 Create Droplet**
```bash
# Go to DigitalOcean Dashboard
# Click "Create" → "Droplets"

# Configuration:
- Image: Ubuntu 22.04 LTS
- Size: 4GB RAM, 2 vCPUs, 80GB SSD (Minimum)
- Datacenter: Choose closest to your users
- Authentication: SSH Key (Recommended)
- Hostname: erp-system-prod
- Tags: erp-system, production
```

#### **1.2 Connect to Droplet**
```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y
```

### **STEP 2: INSTALL DOCKER & DOCKER COMPOSE**

#### **2.1 Install Docker**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
usermod -aG docker $USER

# Start Docker service
systemctl start docker
systemctl enable docker
```

#### **2.2 Install Docker Compose**
```bash
# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### **STEP 3: DEPLOY APPLICATION**

#### **3.1 Clone Repository**
```bash
# Create application directory
mkdir -p /opt/erp-system
cd /opt/erp-system

# Clone repository (replace with your repo URL)
git clone https://github.com/yourusername/integrated-erp-system.git .

# Or upload files using SCP
# scp -r /path/to/integrated-erp-system root@YOUR_DROPLET_IP:/opt/erp-system/
```

#### **3.2 Configure Environment**
```bash
# Copy environment file
cp env.production.example .env

# Edit environment variables
nano .env
```

#### **3.3 Update Environment Variables**
```bash
# Edit .env file with your production values
nano .env

# Required changes:
POSTGRES_PASSWORD=your_secure_postgres_password_here
REDIS_PASSWORD=your_secure_redis_password_here
SECRET_KEY=your_super_secret_key_change_in_production_minimum_32_characters
JWT_SECRET_KEY=your_jwt_secret_key_change_in_production_minimum_32_characters
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### **3.4 Deploy Application**
```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### **STEP 4: CONFIGURE DOMAIN & SSL**

#### **4.1 Point Domain to Droplet**
```bash
# In your domain registrar:
# Add A record: yourdomain.com → YOUR_DROPLET_IP
# Add A record: www.yourdomain.com → YOUR_DROPLET_IP
```

#### **4.2 Install SSL Certificate**
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Stop nginx container
docker-compose -f docker/docker-compose.production.yml stop nginx

# Get SSL certificate
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Update nginx configuration
nano docker/nginx/nginx.production.conf
# Uncomment HTTPS server block and update SSL paths
```

### **STEP 5: CONFIGURE FIREWALL**

#### **5.1 Setup UFW Firewall**
```bash
# Install UFW
apt install ufw -y

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Check status
ufw status
```

---

## 🚀 **OPTION 2: KUBERNETES DEPLOYMENT**

### **STEP 1: CREATE KUBERNETES CLUSTER**

#### **1.1 Create DOKS Cluster**
```bash
# Go to DigitalOcean Dashboard
# Click "Create" → "Kubernetes"

# Configuration:
- Version: Latest stable
- Region: Choose closest to your users
- Node Pool: 3 nodes, 4GB RAM, 2 vCPUs
- Tags: erp-system, production
```

#### **1.2 Connect to Cluster**
```bash
# Install doctl
snap install doctl

# Authenticate
doctl auth init

# Get kubeconfig
doctl kubernetes cluster kubeconfig save YOUR_CLUSTER_ID
```

### **STEP 2: DEPLOY TO KUBERNETES**

#### **2.1 Create Namespace**
```bash
# Create namespace
kubectl create namespace erp-system
kubectl config set-context --current --namespace=erp-system
```

#### **2.2 Deploy Application**
```bash
# Create ConfigMap for environment variables
kubectl create configmap erp-config --from-env-file=.env

# Deploy PostgreSQL
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

# Deploy Redis
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml

# Deploy Backend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# Deploy Frontend
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# Deploy Nginx
kubectl apply -f k8s/nginx-deployment.yaml
kubectl apply -f k8s/nginx-service.yaml
```

---

## 📊 **MONITORING SETUP**

### **STEP 1: ACCESS MONITORING DASHBOARDS**

#### **1.1 Grafana Dashboard**
```bash
# Access Grafana
http://YOUR_DROPLET_IP:3001
# Username: admin
# Password: admin123 (change in production)
```

#### **1.2 Prometheus Metrics**
```bash
# Access Prometheus
http://YOUR_DROPLET_IP:9090
```

#### **1.3 Kibana Logs**
```bash
# Access Kibana
http://YOUR_DROPLET_IP:5601
```

### **STEP 2: CONFIGURE ALERTS**

#### **2.1 Setup Email Alerts**
```bash
# Edit Grafana configuration
docker-compose -f docker/docker-compose.production.yml exec grafana grafana-cli admin reset-admin-password your_new_password

# Configure SMTP in Grafana
# Go to Administration → Settings → SMTP
```

---

## 🔧 **MANAGEMENT COMMANDS**

### **✅ DROPLET MANAGEMENT**

#### **Start Services:**
```bash
docker-compose -f docker/docker-compose.production.yml up -d
```

#### **Stop Services:**
```bash
docker-compose -f docker/docker-compose.production.yml down
```

#### **Restart Services:**
```bash
docker-compose -f docker/docker-compose.production.yml restart
```

#### **View Logs:**
```bash
docker-compose -f docker/docker-compose.production.yml logs -f
```

#### **Update System:**
```bash
./scripts/update.sh
```

#### **Create Backup:**
```bash
./scripts/backup.sh
```

### **✅ KUBERNETES MANAGEMENT**

#### **Check Pod Status:**
```bash
kubectl get pods
```

#### **View Logs:**
```bash
kubectl logs -f deployment/backend
kubectl logs -f deployment/frontend
```

#### **Scale Services:**
```bash
kubectl scale deployment backend --replicas=3
kubectl scale deployment frontend --replicas=2
```

---

## 💰 **COST ESTIMATION**

### **✅ DROPLET DEPLOYMENT COSTS**

| **Droplet Size** | **Monthly Cost** | **Recommended For** |
|------------------|------------------|---------------------|
| **2GB RAM, 1 vCPU** | $12/month | Development, Testing |
| **4GB RAM, 2 vCPUs** | $24/month | Small Business |
| **8GB RAM, 4 vCPUs** | $48/month | Medium Business |
| **16GB RAM, 8 vCPUs** | $96/month | Large Business |

### **✅ KUBERNETES DEPLOYMENT COSTS**

| **Cluster Size** | **Monthly Cost** | **Recommended For** |
|-------------------|------------------|---------------------|
| **3 nodes, 4GB each** | $60/month | Small Business |
| **5 nodes, 8GB each** | $200/month | Medium Business |
| **10 nodes, 16GB each** | $800/month | Large Business |

---

## 🔒 **SECURITY CONFIGURATION**

### **STEP 1: SECURE DROPLET**

#### **1.1 Update System**
```bash
apt update && apt upgrade -y
```

#### **1.2 Configure SSH**
```bash
# Edit SSH config
nano /etc/ssh/sshd_config

# Disable root login
PermitRootLogin no

# Restart SSH
systemctl restart ssh
```

#### **1.3 Install Fail2Ban**
```bash
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

### **STEP 2: CONFIGURE SSL**

#### **2.1 Install Certbot**
```bash
apt install certbot python3-certbot-nginx -y
```

#### **2.2 Get SSL Certificate**
```bash
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

#### **2.3 Auto-renewal**
```bash
# Add to crontab
crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📋 **POST-DEPLOYMENT CHECKLIST**

### **✅ DEPLOYMENT VERIFICATION**

#### **1. Service Health:**
- [ ] All services running
- [ ] Health checks passing
- [ ] Database connectivity
- [ ] Redis connectivity
- [ ] API endpoints responding

#### **2. Security:**
- [ ] SSL certificates configured
- [ ] Security headers enabled
- [ ] Rate limiting active
- [ ] Authentication working
- [ ] Authorization configured

#### **3. Monitoring:**
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards working
- [ ] Logs being collected
- [ ] Alerts configured
- [ ] Performance monitoring active

#### **4. Backup:**
- [ ] Database backup configured
- [ ] File backup configured
- [ ] Backup schedule set
- [ ] Backup retention configured
- [ ] Restore process tested

---

## 🎉 **DEPLOYMENT COMPLETE**

**✅ INDEPENDENT ERP SYSTEM DEPLOYED ON DIGITALOCEAN!**

### **Access URLs:**
- **Main Application**: https://yourdomain.com
- **Grafana**: https://yourdomain.com:3001
- **Prometheus**: https://yourdomain.com:9090
- **Kibana**: https://yourdomain.com:5601

### **Management:**
- **SSH Access**: `ssh root@YOUR_DROPLET_IP`
- **Docker Management**: Use provided scripts
- **Monitoring**: Access Grafana dashboards
- **Backups**: Automated daily backups

**The system is now running in production on DigitalOcean!** 🚀
