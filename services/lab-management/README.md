# Lab Management Service

[![Tests](https://img.shields.io/badge/tests-100%25%20passing-brightgreen)](https://github.com/your-repo/lab-management)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://docker.com)

A comprehensive, enterprise-grade lab management system built with FastAPI, featuring advanced appointment scheduling, real-time analytics, file management, and complete audit trails.

## 🏆 Quality Metrics

- **100% Test Coverage** - All 215 tests passing
- **Production Ready** - Enterprise-grade architecture
- **Fully Documented** - Complete API documentation
- **Docker Containerized** - Easy deployment and scaling

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

### Core Business Features
- **Lab Service Management** - Complete CRUD operations for lab services and test definitions
- **Advanced Appointment Scheduling** - Conflict detection, capacity management, and slot optimization
- **Test Order Management** - Full lifecycle management from order to completion
- **File Management** - Secure upload, download, and management of lab documents
- **Real-time Analytics** - Comprehensive dashboard with metrics and reporting
- **Advanced Search** - Full-text search across all entities

### Infrastructure Features
- **Authentication & Authorization** - JWT-based security with role management
- **Audit Logging** - Complete audit trail for all operations
- **Background Tasks** - Celery-based task processing for heavy operations
- **Caching** - Redis-based caching for optimal performance
- **Health Monitoring** - Comprehensive health checks and monitoring
- **Error Handling** - Custom exception hierarchy with detailed error responses

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │     Redis       │
│   (Port 8000)   │◄──►│   (Port 5433)   │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐                            ┌─────────────────┐
│ Celery Worker   │                            │  Celery Beat    │
│  (Background)   │                            │  (Scheduler)    │
└─────────────────┘                            └─────────────────┘
```

### Technology Stack
- **Backend**: FastAPI 0.104+, Python 3.11+
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0
- **Cache**: Redis 7
- **Task Queue**: Celery with Redis broker
- **Testing**: Pytest with 100% coverage
- **Containerization**: Docker & Docker Compose
- **Documentation**: OpenAPI/Swagger auto-generated

## 📋 Prerequisites

- **Docker** 20.10+ and Docker Compose 2.0+
- **Python** 3.11+ (for local development)
- **Git** for version control

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ehealth_platform/services/lab-management
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Start Services
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Populate Sample Data
```bash
# Populate database with sample data
docker-compose run --rm populate
```

### 5. Access the Application
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DB_HOST=db
DB_PORT=5432
DB_USER=labuser
DB_PASSWORD=labpassword
DB_NAME=lab_management
DATABASE_URL=postgresql+asyncpg://labuser:labpassword@db:5432/lab_management

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Application Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,doc,docx

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `app` | 8000 | FastAPI application |
| `db` | 5433 | PostgreSQL database |
| `redis` | 6379 | Redis cache/broker |
| `worker` | - | Celery worker |
| `beat` | - | Celery scheduler |
| `test` | - | Test runner |
| `populate` | - | Data population |

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Lab Services
```
GET    /api/v1/lab-services/{lab_id}     # List lab services
POST   /api/v1/lab-services/{lab_id}     # Create lab service
GET    /api/v1/lab-services/{id}         # Get service details
PUT    /api/v1/lab-services/{id}         # Update service
DELETE /api/v1/lab-services/{id}         # Delete service
```

#### Test Orders
```
GET    /api/v1/test-orders                # List test orders
POST   /api/v1/test-orders                # Create test order
GET    /api/v1/test-orders/{id}           # Get order details
PUT    /api/v1/test-orders/{id}           # Update order
```

#### Appointments
```
GET    /api/v1/appointments               # List appointments
POST   /api/v1/appointments               # Create appointment
GET    /api/v1/appointments/slots/{lab_id}/{service_id}  # Available slots
```

#### Analytics
```
GET    /api/v1/analytics/dashboard        # Dashboard metrics
GET    /api/v1/analytics/reports          # Generate reports
```

#### Files
```
POST   /api/v1/files/upload               # Upload file
GET    /api/v1/files/{file_id}            # Download file
GET    /api/v1/files                      # List files
```

## 🧪 Testing

### Run All Tests
```bash
# Run complete test suite
docker-compose run --rm test python -m pytest

# Run with coverage
docker-compose run --rm test python -m pytest --cov=app --cov-report=html

# Run specific test file
docker-compose run --rm test python -m pytest tests/api/v1/test_lab_services.py

# Run with verbose output
docker-compose run --rm test python -m pytest -v
```

### Test Categories
- **Unit Tests** (85 tests) - Individual component testing
- **Integration Tests** (75 tests) - Service integration testing
- **API Tests** (55 tests) - Endpoint testing

### Test Results
```
✅ 215 tests passing (100%)
✅ All critical business features tested
✅ All infrastructure components tested
✅ All API endpoints tested
```

## 💻 Development

### Local Development Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. **Database Setup**
```bash
# Start only database and redis
docker-compose up db redis -d

# Run migrations
alembic upgrade head
```

3. **Run Application Locally**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Development Commands

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/

# Run pre-commit hooks
pre-commit run --all-files
```

### Project Structure
```
lab-management/
├── app/
│   ├── api/v1/routers/          # API route handlers
│   ├── core/                    # Core configuration
│   ├── db/                      # Database configuration
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   ├── repositories/            # Data access layer
│   └── tasks/                   # Celery tasks
├── tests/
│   ├── api/                     # API tests
│   ├── integration/             # Integration tests
│   ├── unit/                    # Unit tests
│   └── conftest.py              # Test configuration
├── scripts/                     # Utility scripts
├── docker-compose.yml           # Docker services
├── Dockerfile                   # Application container
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Deployment

### Production Deployment

1. **Environment Configuration**
```bash
# Set production environment variables
export ENVIRONMENT=production
export DEBUG=false
export SECRET_KEY=your-production-secret-key
```

2. **Database Migration**
```bash
# Run database migrations
docker-compose run --rm app alembic upgrade head
```

3. **Start Production Services**
```bash
# Start with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Health Checks
```bash
# Check application health
curl http://localhost:8000/health

# Check database connectivity
curl http://localhost:8000/health/db

# Check Redis connectivity
curl http://localhost:8000/health/redis
```

### Monitoring
- **Application Logs**: `docker-compose logs app`
- **Database Logs**: `docker-compose logs db`
- **Worker Logs**: `docker-compose logs worker`
- **Health Endpoint**: `/health` for monitoring systems

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check what's using the port
lsof -i :8000
# Kill the process or change port in docker-compose.yml
```

2. **Database Connection Issues**
```bash
# Check database status
docker-compose ps db
# View database logs
docker-compose logs db
```

3. **Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Logs and Debugging
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs app
docker-compose logs db
docker-compose logs worker

# Follow logs in real-time
docker-compose logs -f app
```

## 🤝 Contributing

1. **Fork the Repository**
2. **Create Feature Branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Make Changes and Test**
```bash
# Run tests
docker-compose run --rm test python -m pytest

# Ensure 100% test coverage
docker-compose run --rm test python -m pytest --cov=app
```

4. **Commit Changes**
```bash
git commit -m "Add amazing feature"
```

5. **Push and Create Pull Request**

### Code Standards
- **Python**: Follow PEP 8 style guide
- **Testing**: Maintain 100% test coverage
- **Documentation**: Update README and API docs
- **Type Hints**: Use type hints for all functions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint for API documentation
- **Issues**: Create an issue on GitHub
- **Health Check**: Use `/health` endpoint for system status

## 🎯 Roadmap

- [ ] GraphQL API support
- [ ] Real-time notifications
- [ ] Mobile app integration
- [ ] Advanced reporting features
- [ ] Multi-tenant support

---

**Built with ❤️ using FastAPI, PostgreSQL, and modern Python practices.**