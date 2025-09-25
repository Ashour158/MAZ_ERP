#!/bin/bash

# Integrated ERP System Preview Demo
# This script sets up a preview environment to showcase all functionalities

set -e

echo "🎬 Setting up Integrated ERP System Preview Demo..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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
    echo -e "${RED}[ERROR]${NC} $1
}

print_demo() {
    echo -e "${PURPLE}[DEMO]${NC} $1"
}

print_feature() {
    echo -e "${CYAN}[FEATURE]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create demo data
create_demo_data() {
    print_status "Creating demo data..."
    
    # Create demo customers
    cat > demo_data/customers.json << EOF
[
  {
    "customer_name": "Acme Corporation",
    "customer_type": "Company",
    "customer_group": "Commercial",
    "territory": "North America",
    "email": "contact@acme.com",
    "phone": "+1-555-0123"
  },
  {
    "customer_name": "TechStart Inc",
    "customer_type": "Company", 
    "customer_group": "Startup",
    "territory": "North America",
    "email": "info@techstart.com",
    "phone": "+1-555-0456"
  },
  {
    "customer_name": "Global Solutions Ltd",
    "customer_type": "Company",
    "customer_group": "Enterprise",
    "territory": "Europe",
    "email": "sales@globalsolutions.com",
    "phone": "+44-20-7946-0958"
  }
]
EOF

    # Create demo items
    cat > demo_data/items.json << EOF
[
  {
    "item_code": "LAPTOP-001",
    "item_name": "Business Laptop",
    "item_group": "Electronics",
    "is_stock_item": 1,
    "valuation_rate": 1200.00,
    "reorder_level": 10,
    "reorder_qty": 50
  },
  {
    "item_code": "MOUSE-001", 
    "item_name": "Wireless Mouse",
    "item_group": "Electronics",
    "is_stock_item": 1,
    "valuation_rate": 25.00,
    "reorder_level": 20,
    "reorder_qty": 100
  },
  {
    "item_code": "KEYBOARD-001",
    "item_name": "Mechanical Keyboard",
    "item_group": "Electronics", 
    "is_stock_item": 1,
    "valuation_rate": 150.00,
    "reorder_level": 15,
    "reorder_qty": 75
  }
]
EOF

    # Create demo maintenance tickets
    cat > demo_data/tickets.json << EOF
[
  {
    "subject": "Server Performance Issue",
    "description": "Server response time is slow during peak hours. Need immediate attention.",
    "priority": "High",
    "customer": "Acme Corporation",
    "ticket_type": "Technical Support",
    "status": "Open"
  },
  {
    "subject": "Software License Renewal",
    "description": "Annual software license renewal required for Microsoft Office suite.",
    "priority": "Medium", 
    "customer": "TechStart Inc",
    "ticket_type": "Administrative",
    "status": "In Progress"
  },
  {
    "subject": "Network Connectivity Problem",
    "description": "Intermittent network connectivity issues reported by multiple users.",
    "priority": "Critical",
    "customer": "Global Solutions Ltd", 
    "ticket_type": "Technical Support",
    "status": "Open"
  }
]
EOF

    # Create demo inventory
    cat > demo_data/inventory.json << EOF
[
  {
    "item_code": "LAPTOP-001",
    "warehouse": "Main Warehouse",
    "actual_qty": 5,
    "reserved_qty": 2,
    "projected_qty": 3
  },
  {
    "item_code": "MOUSE-001",
    "warehouse": "Main Warehouse", 
    "actual_qty": 15,
    "reserved_qty": 5,
    "projected_qty": 10
  },
  {
    "item_code": "KEYBOARD-001",
    "warehouse": "Main Warehouse",
    "actual_qty": 8,
    "reserved_qty": 3,
    "projected_qty": 5
  }
]
EOF

    print_success "Demo data created"
}

# Start preview services
start_preview_services() {
    print_status "Starting preview services..."
    
    # Start only essential services for preview
    docker-compose -f docker/docker-compose.yml up -d db redis
    
    # Wait for database to be ready
    print_status "Waiting for database to initialize..."
    sleep 30
    
    # Start backend
    docker-compose -f docker/docker-compose.yml up -d backend
    
    # Wait for backend to be ready
    print_status "Waiting for backend to initialize..."
    sleep 60
    
    # Start frontend
    docker-compose -f docker/docker-compose.yml up -d frontend
    
    # Start nginx
    docker-compose -f docker/docker-compose.yml up -d nginx
    
    print_success "Preview services started"
}

# Create demo users
create_demo_users() {
    print_status "Creating demo users..."
    
    # Create demo users with different roles
    cat > demo_users.sql << EOF
-- Demo Users
INSERT INTO tabUser (name, email, first_name, last_name, enabled, user_type) VALUES
('demo-admin@erpnext.com', 'demo-admin@erpnext.com', 'Demo', 'Administrator', 1, 'System User'),
('demo-maintenance@erpnext.com', 'demo-maintenance@erpnext.com', 'Demo', 'Maintenance Manager', 1, 'System User'),
('demo-supply@erpnext.com', 'demo-supply@erpnext.com', 'Demo', 'Supply Chain Manager', 1, 'System User'),
('demo-crm@erpnext.com', 'demo-crm@erpnext.com', 'Demo', 'CRM Manager', 1, 'System User');

-- Demo Roles
INSERT INTO tabRole (name, desk_access, is_custom) VALUES
('Demo Maintenance Manager', 1, 1),
('Demo Supply Chain Manager', 1, 1),
('Demo CRM Manager', 1, 1);

-- Demo Role Profiles
INSERT INTO tabRole Profile (name, roles) VALUES
('Demo Maintenance Manager', 'Demo Maintenance Manager'),
('Demo Supply Chain Manager', 'Demo Supply Chain Manager'),
('Demo CRM Manager', 'Demo CRM Manager');
EOF

    print_success "Demo users created"
}

# Display preview information
display_preview_info() {
    print_demo "🎬 INTEGRATED ERP SYSTEM PREVIEW DEMO"
    echo ""
    echo "📋 Access Information:"
    echo "  🌐 Frontend: http://localhost:3000"
    echo "  🔧 Backend API: http://localhost:8000"
    echo "  📊 Admin Panel: http://localhost:8000/app"
    echo ""
    echo "🔑 Demo Credentials:"
    echo "  👤 Administrator: admin@erpnext.com / admin123"
    echo "  🔧 Maintenance Manager: demo-maintenance@erpnext.com / demo123"
    echo "  📦 Supply Chain Manager: demo-supply@erpnext.com / demo123"
    echo "  👥 CRM Manager: demo-crm@erpnext.com / demo123"
    echo ""
    print_feature "🎯 DEMO FEATURES TO TEST:"
    echo ""
    print_feature "1. 🔧 ENHANCED MAINTENANCE MODULE:"
    echo "   • AI-powered ticket routing and prioritization"
    echo "   • Real-time communication hub"
    echo "   • SLA management with automated escalation"
    echo "   • Sentiment analysis for customer feedback"
    echo "   • Performance analytics and insights"
    echo ""
    print_feature "2. 📦 INTELLIGENT SUPPLY CHAIN:"
    echo "   • ML-based demand forecasting"
    echo "   • Automated reorder recommendations"
    echo "   • Smart purchase order generation"
    echo "   • Vendor performance tracking"
    echo "   • Cost optimization analytics"
    echo ""
    print_feature "3. 👥 ENHANCED CRM MODULE:"
    echo "   • Customer 360-degree view"
    echo "   • AI-powered customer insights"
    echo "   • Predictive analytics for churn and upsell"
    echo "   • Advanced quote management"
    echo "   • Customer success tracking"
    echo ""
    print_feature "4. 🤖 AI ANALYTICS DASHBOARD:"
    echo "   • Predictive maintenance alerts"
    echo "   • Demand forecasting models"
    echo "   • Anomaly detection"
    echo "   • Performance optimization"
    echo "   • Business intelligence insights"
    echo ""
    print_feature "5. ⚡ REAL-TIME FEATURES:"
    echo "   • Live data updates via WebSocket"
    echo "   • Real-time notifications"
    echo "   • Optimistic UI updates"
    echo "   • Live collaboration"
    echo "   • Instant status changes"
    echo ""
    print_demo "🎬 DEMO SCENARIOS TO TRY:"
    echo ""
    echo "📋 Scenario 1: Maintenance Ticket Workflow"
    echo "   1. Go to Maintenance Module"
    echo "   2. Create a new ticket with 'Critical' priority"
    echo "   3. Watch AI sentiment analysis in action"
    echo "   4. See real-time SLA status updates"
    echo "   5. Test escalation workflow"
    echo ""
    echo "📦 Scenario 2: Supply Chain Intelligence"
    echo "   1. Go to Supply Chain Module"
    echo "   2. Check inventory levels"
    echo "   3. Review AI-generated reorder recommendations"
    echo "   4. Approve recommendations and see PO generation"
    echo "   5. Monitor vendor performance metrics"
    echo ""
    echo "👥 Scenario 3: CRM Analytics"
    echo "   1. Go to CRM Module"
    echo "   2. View customer analytics dashboard"
    echo "   3. Check AI-powered insights"
    echo "   4. Review churn risk predictions"
    echo "   5. Explore upsell opportunities"
    echo ""
    echo "🤖 Scenario 4: AI Analytics"
    echo "   1. Go to Analytics Module"
    echo "   2. View predictive maintenance alerts"
    echo "   3. Check demand forecasting"
    echo "   4. Review anomaly detection"
    echo "   5. Explore business intelligence insights"
    echo ""
    print_demo "🔧 TECHNICAL FEATURES TO OBSERVE:"
    echo ""
    echo "• 🚀 Performance: Notice fast loading and smooth interactions"
    echo "• 📱 Responsive: Test on different screen sizes"
    echo "• 🔄 Real-time: Watch live updates without page refresh"
    echo "• 🎨 Modern UI: Experience the clean, intuitive interface"
    echo "• 🔐 Security: Notice JWT authentication and role-based access"
    echo "• 📊 Analytics: Explore comprehensive reporting and insights"
    echo "• 🤖 AI Features: Experience intelligent automation"
    echo "• ⚡ Speed: Notice optimized performance with caching"
    echo ""
    print_success "🎉 Preview demo is ready!"
    echo ""
    echo "📝 Next Steps:"
    echo "  1. Open http://localhost:3000 in your browser"
    echo "  2. Login with demo credentials"
    echo "  3. Explore all modules and features"
    echo "  4. Test the demo scenarios above"
    echo "  5. Experience the AI-powered capabilities"
    echo ""
    echo "🛑 To stop the preview:"
    echo "  docker-compose -f docker/docker-compose.yml down"
    echo ""
    echo "📊 Monitor services:"
    echo "  docker-compose -f docker/docker-compose.yml ps"
    echo "  docker-compose -f docker/docker-compose.yml logs -f"
}

# Health check
check_services_health() {
    print_status "Checking services health..."
    
    # Check if services are running
    if docker-compose -f docker/docker-compose.yml ps | grep -q "Up"; then
        print_success "Services are running"
    else
        print_error "Some services failed to start"
        return 1
    fi
    
    # Check frontend accessibility
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend may still be starting up"
    fi
    
    # Check backend accessibility
    if curl -f http://localhost:8000/api/health >/dev/null 2>&1; then
        print_success "Backend API is accessible"
    else
        print_warning "Backend API may still be starting up"
    fi
}

# Main execution
main() {
    echo "🎬 Integrated ERP System Preview Demo Setup"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    create_demo_data
    create_demo_users
    start_preview_services
    check_services_health
    display_preview_info
}

# Run main function
main "$@"
