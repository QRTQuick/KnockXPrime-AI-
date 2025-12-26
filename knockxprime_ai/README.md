# KnockXPrime AI - Neon Database Integration

A FastAPI-based AI chat service with subscription management, user authentication, and usage tracking using Neon Database.

## Features

- 🔐 **User Authentication**: JWT tokens and API key authentication
- 💳 **Subscription Plans**: Tiered pricing with usage limits
- 📊 **Usage Tracking**: Real-time token and request monitoring
- 🤖 **Grok AI Integration**: Chat completions with billing enforcement
- 🗄️ **Neon Database**: PostgreSQL database for user data and analytics
- 🚀 **Render Deployment**: Keep-alive endpoints for cloud hosting

## Subscription Plans

| Plan Name | Price | Max Tokens/Day | Max Requests/Day | Notes             |
| --------- | ----- | -------------- | ---------------- | ----------------- |
| Baby Free | $0    | 1,000          | 10/day           | Free limited plan |
| Leveler   | $4    | 5,000          | 100/day          | Paid              |
| Log Min   | $10   | 20,000         | 500/day          | Paid              |
| High Max  | $100  | 100,000        | 2,000/day        | Paid              |

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to project
cd knockxprime_ai

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your Neon REST API credentials:

```env
# Neon Database REST API Configuration
NEON_API_URL=https://ep-ancient-mountain-afykb78o.apirest.c-2.us-west-2.aws.neon.tech/neondb/rest/v1
NEON_API_KEY=your_neon_api_key_here

# Grok API Configuration
GROK_API_KEY=your_grok_api_key_here

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Environment
ENVIRONMENT=production
```

### 3. Initialize Database

```bash
# Run database setup script
python setup_database.py
```

### 4. Run the Application

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Using Docker
docker-compose up -d
```

### 5. Test the API

```bash
# Run the test script
python test_api.py

# Or visit the interactive docs
# http://localhost:8000/docs
```

## API Endpoints

### Authentication
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - Login user
- `GET /api/v1/users/profile` - Get user profile
- `POST /api/v1/users/regenerate-api-key` - Regenerate API key

### Chat
- `POST /api/v1/chat/completions` - Chat completions with billing
- `GET /api/v1/chat/usage` - Current usage info

### Plans
- `GET /api/v1/plans/` - List all subscription plans
- `GET /api/v1/plans/{plan_id}` - Get specific plan
- `POST /api/v1/plans/upgrade` - Upgrade subscription plan
- `GET /api/v1/plans/compare/pricing` - Compare plans

### Usage Analytics
- `GET /api/v1/usage/current` - Current month usage
- `GET /api/v1/usage/history` - Usage history
- `GET /api/v1/usage/stats` - Detailed analytics

### Admin (Restricted)
- `GET /api/v1/admin/stats/overview` - Admin dashboard
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/usage/top-users` - Top users by usage
- `POST /api/v1/admin/users/{user_id}/reset-usage` - Reset user usage

### Health
- `GET /health/` - Health check
- `GET /health/ping` - Simple ping
- `GET /health/database` - Neon database connection test

## Usage Example

### 1. Register User

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword",
    "plan_name": "Leveler"
  }'
```

### 2. Chat Request

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "max_tokens": 100
  }'
```

## Database Integration

### Neon PostgreSQL 15 REST API
- Uses Neon's REST API endpoint instead of direct PostgreSQL connection
- Automatic retry logic for transient failures
- Proper error handling and logging
- Connection health monitoring

### API Endpoint
```
https://ep-ancient-mountain-afykb78o.apirest.c-2.us-west-2.aws.neon.tech/neondb/rest/v1
```

### Database Schema

### Tables
- **users**: User accounts and authentication
- **plans**: Subscription plans and pricing
- **usage**: Monthly usage tracking
- **sessions**: Optional session storage

## Production Features

### Security & Performance
- Rate limiting (100 requests/minute per IP/API key)
- Request/response logging middleware
- JWT token authentication with API keys
- Password hashing with bcrypt
- SQL injection protection
- CORS configuration

### Admin Dashboard
- User management and statistics
- Usage analytics and top users
- Revenue estimation
- System health monitoring
- User usage reset capabilities

### Monitoring & Deployment
- Docker containerization
- Health check endpoints
- Automatic database initialization
- Keep-alive for Render deployment
- Comprehensive error handling

## Testing

The project includes a comprehensive test script:

```bash
python test_api.py
```

This will test:
- Health endpoints
- User registration and login
- API key authentication
- Plans listing
- Chat endpoint (requires Grok API key)

## Deployment

### Render.com
1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Deploy with automatic builds

### Keep-Alive
The `/health/` endpoint prevents Render free tier from sleeping.

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- API key validation
- SQL injection protection with parameterized queries
- CORS middleware configuration

## License

KnockXPrime AI Proprietary License
- Source code is property of the owner
- Unauthorized commercial use prohibited
- Contact for licensing or collaboration

## Support

For issues or questions, please contact the development team.