# 🎬 Integrated ERP System Preview Guide

This guide will help you set up and explore the Integrated ERP System preview to see all functionalities in action.

## 🚀 Quick Start (Windows)

### Option 1: PowerShell Script (Recommended)
```powershell
# Navigate to the integrated-erp-system directory
cd integrated-erp-system

# Run the quick preview script
.\scripts\quick-preview.ps1
```

### Option 2: Manual Setup
```powershell
# Start the services
docker-compose -f docker/docker-compose.yml up -d

# Wait for services to be ready (about 2-3 minutes)
# Then open http://localhost:3000
```

## 🐧 Linux/Mac Setup

```bash
# Navigate to the integrated-erp-system directory
cd integrated-erp-system

# Make scripts executable
chmod +x scripts/*.sh

# Run the preview demo
./scripts/preview-demo.sh
```

## 🌐 Access Information

Once the services are running, you can access:

- **🌐 Frontend Application**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8000
- **📊 Admin Panel**: http://localhost:8000/app

## 🔑 Demo Credentials

### Default Admin
- **Username**: `admin@erpnext.com`
- **Password**: `admin123`

### Demo Users (Different Roles)
- **Maintenance Manager**: `demo-maintenance@erpnext.com` / `demo123`
- **Supply Chain Manager**: `demo-supply@erpnext.com` / `demo123`
- **CRM Manager**: `demo-crm@erpnext.com` / `demo123`

## 🎯 Demo Features to Test

### 1. 🔧 Enhanced Maintenance Module
**Features to Explore:**
- AI-powered ticket routing and prioritization
- Real-time communication hub
- SLA management with automated escalation
- Sentiment analysis for customer feedback
- Performance analytics and insights

**Demo Scenario:**
1. Go to Maintenance Module
2. Create a new ticket with 'Critical' priority
3. Watch AI sentiment analysis in action
4. See real-time SLA status updates
5. Test escalation workflow

### 2. 📦 Intelligent Supply Chain
**Features to Explore:**
- ML-based demand forecasting
- Automated reorder recommendations
- Smart purchase order generation
- Vendor performance tracking
- Cost optimization analytics

**Demo Scenario:**
1. Go to Supply Chain Module
2. Check inventory levels
3. Review AI-generated reorder recommendations
4. Approve recommendations and see PO generation
5. Monitor vendor performance metrics

### 3. 👥 Enhanced CRM Module
**Features to Explore:**
- Customer 360-degree view
- AI-powered customer insights
- Predictive analytics for churn and upsell
- Advanced quote management
- Customer success tracking

**Demo Scenario:**
1. Go to CRM Module
2. View customer analytics dashboard
3. Check AI-powered insights
4. Review churn risk predictions
5. Explore upsell opportunities

### 4. 🤖 AI Analytics Dashboard
**Features to Explore:**
- Predictive maintenance alerts
- Demand forecasting models
- Anomaly detection
- Performance optimization
- Business intelligence insights

**Demo Scenario:**
1. Go to Analytics Module
2. View predictive maintenance alerts
3. Check demand forecasting
4. Review anomaly detection
5. Explore business intelligence insights

### 5. ⚡ Real-time Features
**Features to Explore:**
- Live data updates via WebSocket
- Real-time notifications
- Optimistic UI updates
- Live collaboration
- Instant status changes

## 🔧 Technical Features to Observe

### Performance
- **🚀 Fast Loading**: Notice quick page loads and smooth interactions
- **📱 Responsive**: Test on different screen sizes (mobile, tablet, desktop)
- **⚡ Optimized**: Experience caching and performance optimizations

### User Experience
- **🎨 Modern UI**: Clean, intuitive interface with modern design
- **🔄 Real-time**: Watch live updates without page refresh
- **📊 Interactive**: Explore interactive dashboards and charts

### Security
- **🔐 Authentication**: JWT-based secure authentication
- **👥 Role-based Access**: Different permissions for different users
- **🛡️ Data Protection**: Secure data handling and encryption

### AI/ML Features
- **🤖 Intelligent Automation**: AI-powered recommendations and insights
- **📈 Predictive Analytics**: Forecast trends and predict outcomes
- **🎯 Smart Routing**: Automatic task assignment and prioritization

## 📊 Demo Data Included

The preview includes sample data for testing:

### Customers
- Acme Corporation (Commercial)
- TechStart Inc (Startup)
- Global Solutions Ltd (Enterprise)

### Items
- Business Laptop (LAPTOP-001)
- Wireless Mouse (MOUSE-001)
- Mechanical Keyboard (KEYBOARD-001)

### Maintenance Tickets
- Server Performance Issue (High Priority)
- Software License Renewal (Medium Priority)
- Network Connectivity Problem (Critical Priority)

## 🎬 Step-by-Step Demo Walkthrough

### Step 1: Login and Dashboard
1. Open http://localhost:3000
2. Login with `admin@erpnext.com` / `admin123`
3. Explore the main dashboard
4. Notice the real-time metrics and charts

### Step 2: Maintenance Module
1. Click on "Maintenance Management"
2. Create a new ticket:
   - Subject: "Demo Critical Issue"
   - Priority: "Critical"
   - Description: "This is a demo ticket to test AI features"
3. Watch the AI sentiment analysis
4. See the SLA status updates
5. Test the escalation workflow

### Step 3: Supply Chain Module
1. Click on "Supply Chain Management"
2. Check inventory levels
3. Review AI-generated reorder recommendations
4. Approve a recommendation
5. Watch the purchase order generation

### Step 4: CRM Module
1. Click on "Enhanced CRM"
2. View customer analytics
3. Check AI-powered insights
4. Review churn risk predictions
5. Explore upsell opportunities

### Step 5: AI Analytics
1. Click on "AI Analytics"
2. View predictive maintenance alerts
3. Check demand forecasting
4. Review anomaly detection
5. Explore business intelligence

## 🛠️ Troubleshooting

### Services Not Starting
```bash
# Check Docker status
docker --version
docker-compose --version

# Check running containers
docker-compose -f docker/docker-compose.yml ps

# View logs
docker-compose -f docker/docker-compose.yml logs
```

### Port Conflicts
If ports 3000, 8000, 5432, or 6379 are in use:
```bash
# Stop conflicting services
# Or modify docker-compose.yml to use different ports
```

### Database Issues
```bash
# Reset database
docker-compose -f docker/docker-compose.yml down -v
docker-compose -f docker/docker-compose.yml up -d
```

## 🛑 Stopping the Preview

```bash
# Stop all services
docker-compose -f docker/docker-compose.yml down

# Stop and remove volumes (clean reset)
docker-compose -f docker/docker-compose.yml down -v
```

## 📈 Performance Monitoring

```bash
# Monitor service status
docker-compose -f docker/docker-compose.yml ps

# View real-time logs
docker-compose -f docker/docker-compose.yml logs -f

# Check resource usage
docker stats
```

## 🎯 Key Features to Focus On

### For Business Users
- **Dashboard Analytics**: Real-time business metrics
- **AI Insights**: Intelligent recommendations
- **Workflow Automation**: Streamlined processes
- **Mobile Responsiveness**: Access from any device

### For Technical Users
- **API Integration**: RESTful APIs with WebSocket
- **Real-time Updates**: Live data synchronization
- **Performance**: Optimized loading and caching
- **Security**: JWT authentication and RBAC

### For Administrators
- **User Management**: Role-based access control
- **System Monitoring**: Health checks and metrics
- **Configuration**: Easy setup and deployment
- **Scalability**: Docker-based architecture

## 🎉 Success Indicators

You'll know the preview is working correctly when you see:

✅ **Frontend loads at http://localhost:3000**
✅ **Login works with demo credentials**
✅ **All modules are accessible**
✅ **Real-time updates work**
✅ **AI features are functional**
✅ **Responsive design works on mobile**
✅ **Performance is smooth and fast**

## 📞 Support

If you encounter any issues:

1. **Check the logs**: `docker-compose -f docker/docker-compose.yml logs`
2. **Restart services**: `docker-compose -f docker/docker-compose.yml restart`
3. **Full reset**: `docker-compose -f docker/docker-compose.yml down -v && docker-compose -f docker/docker-compose.yml up -d`

## 🎬 Enjoy Your Preview!

The Integrated ERP System preview showcases a complete, modern ERP solution with:
- **AI-powered automation**
- **Real-time collaboration**
- **Intelligent analytics**
- **Modern user experience**
- **Scalable architecture**

Explore all the features and experience the future of ERP systems! 🚀
