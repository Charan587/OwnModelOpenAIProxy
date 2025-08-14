# BYOM AI Platform - Universal AI Gateway

A comprehensive Bring-Your-Own-Model (BYOM) AI Platform that serves as a universal gateway to multiple AI providers, including OpenAI-compatible services, local Ollama models, and custom HTTP endpoints.

## 🚀 Features

- **Multi-Provider Support**: Connect to OpenAI, Ollama, and custom HTTP endpoints
- **Universal API**: Single OpenAI-compatible endpoint for all models
- **Workspace Isolation**: Multi-tenant architecture with user isolation
- **Rate Limiting**: Redis-based RPM, TPM, and daily caps
- **Usage Tracking**: Comprehensive analytics and monitoring
- **Admin Console**: Beautiful React dashboard for management
- **Security**: JWT authentication, encrypted API keys, role-based access
- **Docker Ready**: Complete containerized deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis         │
                       │   (Rate Limiting)│
                       └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM and database management
- **Redis** - Rate limiting and caching
- **JWT** - Authentication and authorization
- **Argon2** - Password hashing
- **AES-GCM** - API key encryption

### Frontend
- **React 18** - Modern UI framework
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration

## 📁 Project Structure

```
project101/
├── app/                          # Backend application
│   ├── api/                     # API routes
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── providers.py        # Provider management
│   │   ├── models.py           # Model registry
│   │   ├── keys.py             # API key management
│   │   ├── chat.py             # Chat completions
│   │   └── usage.py            # Usage analytics
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Configuration
│   │   ├── security.py         # Security utilities
│   │   ├── db.py              # Database setup
│   │   └── rate_limit.py      # Rate limiting
│   ├── models/                 # Database models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   └── main.py                # FastAPI application
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom React hooks
│   │   └── services/          # API services
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml          # Service orchestration
├── requirements.txt            # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd OwnModelOpenAIProxy
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

**Required Environment Variables:**
```bash
# Security
SECRET_KEY=your-super-secret-key-change-in-production
ENCRYPTION_KEY=your-32-byte-encryption-key-here

# Database
DATABASE_URL=postgresql://byom_user:byom_password@postgres:5432/byom_ai

# Redis
REDIS_URL=redis://redis:6379
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Start with Ollama (optional)
docker-compose --profile ollama up -d
```

### 4. Access the Platform

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432
- **Redis**: localhost:6379

### 5. Initial Setup

1. **Register Account**: Visit http://localhost:3000/register
2. **Create Workspace**: Your first workspace will be created automatically
3. **Add Provider**: Use the admin console to add your first AI provider
4. **Register Models**: Add models from your providers
5. **Create API Key**: Generate API keys for your applications

## 🔧 Local Development

### Backend Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://byom_user:byom_password@localhost:5432/byom_ai"
export REDIS_URL="redis://localhost:6379"

# Run database migrations
python -c "from app.core.db import engine, Base; Base.metadata.create_all(engine)"

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📚 API Usage

### Authentication

```bash
# Register
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "workspace_name": "My Workspace"}'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Chat Completions

```bash
# Use your API key
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "temperature": 0.7
  }'
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Argon2 for secure password storage
- **API Key Encryption**: AES-GCM encryption for provider secrets
- **Rate Limiting**: Redis-based request and token limits
- **Workspace Isolation**: Multi-tenant architecture
- **Role-Based Access**: Admin and user roles

## 📊 Monitoring & Analytics

- **Request Logging**: Complete audit trail of all API calls
- **Usage Metrics**: Token consumption, latency, success rates
- **Provider Health**: Real-time provider status monitoring
- **Cost Tracking**: Optional cost tracking for billing
- **Performance Metrics**: Response times and throughput

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Update all secrets and keys
2. **Database**: Use production PostgreSQL instance
3. **Redis**: Use production Redis cluster
4. **SSL/TLS**: Configure HTTPS endpoints
5. **Monitoring**: Add logging and monitoring solutions
6. **Backup**: Implement database backup strategies

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the API docs at `/docs`
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions

## 🔮 Roadmap

- [ ] Google OAuth integration
- [ ] Advanced analytics dashboard
- [ ] Model fine-tuning support
- [ ] Webhook notifications
- [ ] Multi-region deployment
- [ ] Enterprise SSO
- [ ] Advanced rate limiting strategies
- [ ] Model performance benchmarking

---

**Built with ❤️ for the AI community**
