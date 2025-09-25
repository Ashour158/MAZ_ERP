# 🏢 Integrated ERP System

A comprehensive ERP solution combining ERPNext backend with modern React frontend, featuring AI-powered analytics, real-time updates, and enhanced modules.

## 🚀 Features

### Core Modules
- **Enhanced Maintenance Module** - Advanced ticket system with AI sentiment analysis
- **Supply Chain Module** - Intelligent inventory management with ML recommendations
- **Enhanced CRM Module** - Customer analytics with AI insights
- **AI Analytics Module** - Predictive analytics and recommendation engine

### Technical Features
- **Real-time Updates** - WebSocket connections for live data
- **AI/ML Integration** - Sentiment analysis, demand forecasting, recommendations
- **Modern UI** - React-based responsive interface
- **API Gateway** - RESTful APIs with authentication
- **Performance Optimized** - Caching, query optimization, virtual scrolling

## 🏗️ Architecture

```
Frontend (React/TypeScript) ←→ API Gateway ←→ ERPNext Backend (Python/Frappe)
                                      ↓
                              Database (PostgreSQL)
                                      ↓
                              Cache (Redis)
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd integrated-erp-system
```

2. **Start the system**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/app

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Integration Guide](docs/INTEGRATION.md)

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📊 Modules

### Maintenance Module
- Advanced ticket management
- Communication hub
- SLA management
- Knowledge base
- AI sentiment analysis

### Supply Chain Module
- Inventory management
- Purchase analytics
- Reorder intelligence
- Vendor performance
- Smart PO generation

### Enhanced CRM
- Customer analytics
- Quote management
- Customer success tracking
- AI-powered insights

### AI Analytics
- Predictive analytics
- Recommendation engine
- Anomaly detection
- Performance insights

## 🛡️ Security

- JWT authentication
- Role-based access control
- Data encryption
- API rate limiting
- Input validation

## 📈 Performance

- Redis caching
- Database optimization
- Virtual scrolling
- Lazy loading
- CDN integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details
