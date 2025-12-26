# KnockXPrime AI - Backend API

A FastAPI-based AI chat service with subscription management, user authentication, and usage tracking using Neon Database.

## 🚀 Render Deployment Configuration

### Root Directory
```
knockxprime_ai/
```

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📁 Project Structure

```
knockxprime_ai/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Configuration and settings
│   │   ├── database.py        # Neon DB connection and table creation
│   │   ├── auth.py            # Authentication and JWT handling
│   │   ├── plans.py           # Subscription plan logic
│   │   ├── daily_usage.py     # Daily usage tracking
│   │   ├── neon_utils.py      # Neon API utilities
│   │   └── keep_alive.py      # Health check endpoints
│   ├── api/v1/
│   │   ├── users.py           # User registration, login, profile
│   │   ├── chat.py            # Chat completions with billing
│   │   ├── usage.py           # Usage analytics and history
│   │   ├── plans.py           # Plan management
│   │   └── admin.py           # Admin endpoints
│   ├── services/
│   │   ├── grok_service.py    # Grok API integration
│   │   ├── usage_service.py   # Usage tracking and limits
│   │   └── billing_guard.py   # Subscription enforcement
│   ├── middleware/
│   │   ├── rate_limiting.py   # Rate limiting middleware
│   │   ├── logging.py         # Request logging
│   │   ├── security.py        # Security headers
│   │   └── cors.py            # CORS configuration
│   └── schemas/
│       ├── user_schema.py     # User data models
│       ├── chat_schema.py     # Chat request/response models
│       └── usage_schema.py    # Usage statistics models
├── requirements.txt           # Python dependencies
├── runtime.txt               # Python version
├── Procfile                  # Process configuration
├── gunicorn.conf.py          # Gunicorn configuration
├── render.yaml               # Render service configuration
├── setup_database.py         # Database initialization script
└── README.md                 # This file
```

## 🔧 Environment Variables

### Required Variables
```bash
NEON_API_URL=https://ep-ancient-mountain-afykb78o.apirest.c-2.us-west-2.aws.neon.tech/neondb/rest/v1
NEON_API_KEY=your_neon_api_key_here
GROK_API_KEY=your_grok_api_key_here
SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

### Optional Variables
```bash
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## 💳 Subscription Plans

| Plan Name | Price | Max Tokens/Day | Max Requests/Day | Notes             |
| --------- | ----- | -------------- | ---------------- | ----------------- |
| Baby Free | $0    | 1,000          | 10/day           | Free limited plan |
| Leveler   | $4    | 5,000          | 100/day          | Paid              |
| Log Min   | $10   | 20,000         | 500/day          | Paid              |
| High Max  | $100  | 100,000        | 2,000/day        | Paid              |

## 🛠️ Local Development

### Setup
```bash
# Clone repository
cd knockxprime_ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your actual values

# Initialize database
python setup_database.py

# Run development server
uvicorn app.main:app --reload
```

### Testing
```bash
# Run the API test script
python ../test_api.py

# Or test individual endpoints
curl http://localhost:8000/health/
curl http://localhost:8000/api/v1/plans/
```

## 🌐 API Endpoints

### Health & Info
- `GET /` - API information
- `GET /api` - Detailed API info
- `GET /health/` - Health check
- `GET /health/ping` - Simple ping
- `GET /health/database` - Database connection test
- `GET /health/keep-alive` - Manual keep-alive trigger

### Authentication
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - Login user
- `GET /api/v1/users/profile` - Get user profile
- `POST /api/v1/users/regenerate-api-key` - Regenerate API key

### Chat & AI
- `POST /api/v1/chat/completions` - Chat completions with billing
- `GET /api/v1/chat/usage` - Current usage info

### Plans & Billing
- `GET /api/v1/plans/` - List all subscription plans
- `GET /api/v1/plans/{plan_id}` - Get specific plan
- `POST /api/v1/plans/upgrade` - Upgrade subscription plan
- `GET /api/v1/plans/compare/pricing` - Compare plans

### Usage Analytics
- `GET /api/v1/usage/current` - Current day usage
- `GET /api/v1/usage/daily` - Today's usage statistics
- `GET /api/v1/usage/monthly` - Current month usage
- `GET /api/v1/usage/history` - Usage history
- `GET /api/v1/usage/stats` - Detailed analytics

### Admin (Restricted)
- `GET /api/v1/admin/stats/overview` - Admin dashboard
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/usage/top-users` - Top users by usage
- `POST /api/v1/admin/users/{user_id}/reset-usage` - Reset user usage
- `GET /api/v1/admin/system/health` - System health info

## 🔒 Security Features

### Middleware
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, CSP
- **Rate Limiting**: Configurable requests per minute
- **CORS**: Production-ready CORS configuration
- **Request Logging**: Comprehensive request/response logging

### Authentication
- **JWT Tokens**: Secure token-based authentication
- **API Keys**: Unique API keys for each user
- **Password Hashing**: bcrypt for secure password storage
- **Input Validation**: Pydantic models for request validation

### Database Security
- **Parameterized Queries**: SQL injection protection
- **Connection Encryption**: Secure connections to Neon DB
- **Error Handling**: Secure error responses

## 📊 Performance Features

### Optimization
- **Async/Await**: Non-blocking I/O operations
- **Connection Pooling**: Efficient database connections
- **Caching**: Response caching where appropriate
- **Compression**: Gzip compression for responses

### Monitoring
- **Health Checks**: Multiple health check endpoints
- **Request Tracking**: Request ID tracking
- **Performance Metrics**: Response time headers
- **Error Tracking**: Comprehensive error logging

### Scaling
- **Gunicorn**: Production WSGI server
- **Worker Processes**: Multi-process deployment
- **Keep-Alive**: Automatic service keep-alive
- **Load Balancing**: Ready for horizontal scaling

## 🚀 Deployment on Render

### Automatic Deployment
1. **Connect Repository**: Link your GitHub repository
2. **Service Configuration**:
   - Service Type: Web Service
   - Environment: Python
   - Root Directory: `knockxprime_ai`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**: Set in Render dashboard
   - `NEON_API_URL`
   - `NEON_API_KEY`
   - `GROK_API_KEY`
   - `SECRET_KEY` (auto-generated)

### Manual Deployment
```bash
# Ensure all changes are committed
git add .
git commit -m "Deploy backend to production"
git push origin main

# Render will automatically deploy
```

### Health Monitoring
- Health check endpoint: `/health/`
- Database connectivity: `/health/database`
- Keep-alive mechanism: `/health/keep-alive`

## 🔧 Configuration Files

### render.yaml
Complete Render service configuration with:
- Python environment setup
- Environment variables
- Health check configuration
- CORS headers
- Auto-deploy settings

### gunicorn.conf.py
Production server configuration:
- Worker process management
- Logging configuration
- Performance optimization
- SSL support (if needed)

### Procfile
Process definitions for different deployment platforms

## 📈 Monitoring & Logging

### Request Logging
- Request/response logging
- Performance timing
- Client IP tracking
- Error tracking

### Health Monitoring
- Database connection status
- API response times
- Error rates
- Keep-alive status

### Security Monitoring
- Rate limit violations
- Authentication failures
- Suspicious activity patterns

## 🛡️ Production Checklist

- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] API keys secured
- [ ] Rate limiting configured
- [ ] CORS origins set correctly
- [ ] Health checks responding
- [ ] SSL/HTTPS enabled
- [ ] Error handling tested
- [ ] Performance optimized
- [ ] Security headers enabled
- [ ] Logging configured
- [ ] Monitoring set up

## 📞 Support & Troubleshooting

### Common Issues
1. **Database Connection**: Check NEON_API_KEY and URL
2. **Authentication**: Verify SECRET_KEY is set
3. **Rate Limiting**: Check if hitting request limits
4. **CORS**: Ensure frontend domain is in cors_origins

### Debugging
- Check Render logs in dashboard
- Use `/health/database` to test DB connection
- Monitor `/health/` endpoint for service status
- Review error logs for specific issues

### Performance
- Monitor response times via X-Process-Time header
- Check worker process utilization
- Review database query performance
- Monitor memory usage

## 🎉 Production Ready!

Your KnockXPrime AI backend is now configured for production deployment with:
- ⚡ High-performance async API
- 🔒 Enterprise-grade security
- 📊 Comprehensive monitoring
- 🚀 Auto-scaling capabilities
- 💾 Reliable database integration
- 🛡️ Rate limiting and protection