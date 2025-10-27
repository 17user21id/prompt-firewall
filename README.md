# Prompt Firewall - AI Security Platform

A comprehensive AI security system that protects Large Language Model (LLM) applications from prompt injection attacks and prevents sensitive data exposure in real-time. Built with multi-tenant support, comprehensive audit logging, and an intuitive admin console.

## 🚀 Features

- **Multi-Tenant Architecture**: Complete data isolation and tenant-specific configurations
- **Real-Time PII/PHI Detection**: Advanced pattern matching for emails, SSNs, phone numbers, credit cards, IP addresses, and more
- **Prompt Injection Detection**: Multiple detection methods including heuristic analysis and AI-powered detection
- **Flexible Policy Engine**: Configure custom rules with versioning and priority management
- **Fast API Processing**: High-performance real-time analysis with comprehensive risk scoring
- **Complete Audit Trail**: Full logging for compliance and security monitoring
- **Admin Dashboard**: Web-based interface for comprehensive management and monitoring
- **Python SDK**: Easy integration with existing applications
- **Serverless Architecture**: Scalable deployment on GCP Cloud Run with Firestore backend
- **Dark Mode Support**: Modern UI with automatic theme switching

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Demo UI       │    │  Admin Console  │    │   Python SDK    │
│   (Next.js)     │    │   (Next.js)     │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     FastAPI Backend      │
                    │   (Cloud Run Container)   │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Firewall Engine        │
                    │  ┌─────────────────────┐  │
                    │  │   PII Detector      │  │
                    │  │   Injection Detector│  │
                    │  │   Rules Engine      │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Firestore Database   │
                    │  ┌─────────────────────┐  │
                    │  │   Tenants           │  │
                    │  │   Prompts           │  │
                    │  │   Rules             │  │
                    │  │   Logs              │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Google Cloud Firestore**: Scalable NoSQL database
- **Google Cloud Run**: Serverless container platform
- **Python 3.11+**: Modern Python runtime

### Frontend
- **Next.js 14**: React framework with App Router
- **Tailwind CSS**: Utility-first styling
- **NextAuth.js**: Authentication system
- **React Hot Toast**: User notifications

### AI/ML Security
- **Custom PII Detection**: Regex-based pattern matching for sensitive data
- **Heuristic Analysis**: Pattern-based injection detection
- **OpenAI Integration**: Optional GPT-4 powered detection
- **Anomaly Scoring**: Advanced risk assessment algorithms

### Infrastructure
- **Docker**: Containerization
- **GitHub Actions**: CI/CD automation
- **Firestore**: Managed database
- **Cloud Run**: Auto-scaling serverless platform

## 📁 Project Structure

```
prompt-firewall/
├── backend/                    # FastAPI Backend
│   ├── src/
│   │   ├── api/               # API endpoints
│   │   ├── common/            # Shared utilities
│   │   ├── firewall/         # Detection engine
│   │   ├── models/            # Data models
│   │   ├── store/             # Data layer
│   │   └── main.py            # Application entry
│   ├── requirements.txt       # Dependencies
│   ├── Dockerfile             # Container config
│   └── README.md              # Backend docs
│
├── frontend/                   # Next.js Frontend
│   ├── pages/                 # Page routes
│   ├── components/            # React components
│   ├── lib/                   # Utilities (session, API)
│   └── styles/                # CSS styles
│
├── sdk/                        # Python SDK
│   ├── prompt_firewall/
│   └── setup.py
│
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud SDK
- Docker (optional)

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config.env.example .env
# Edit .env with your configuration

# Run locally
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### SDK Usage

```python
from prompt_firewall import PromptFirewallSDK

# Initialize
sdk = PromptFirewallSDK(
    api_url='http://localhost:8000',
    api_key='your-api-key',
    tenant_id='your-tenant-id'
)

# Process prompt
result = sdk.query("Contact me at john@example.com")
print(f"Decision: {result['decision']}")
print(f"Risks: {result['risks']}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# OpenAI (optional)
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4

# Security
ENCRYPTION_KEY=your-fernet-key
CORS_ORIGINS=["http://localhost:3000"]

# Features
ENABLE_OPENAI_DETECTION=false
ENABLE_RATE_LIMITING=true
```

## 📊 API Endpoints

### Core Endpoints

- `POST /v1/tenants` - Create new tenant
- `POST /v1/tenants/login` - Tenant authentication
- `POST /v1/query` - Process prompt through firewall
- `GET /v1/logs` - Retrieve audit logs
- `GET /v1/prompts` - Get prompt history with filtering
- `GET /v1/rules` - Manage detection rules

### Authentication

All endpoints require Bearer token authentication:
```
Authorization: Bearer <tenant_id>:<api_key>
```

## 🎯 Key Features

### Session Management
- **1-Hour Timeout**: Automatic session expiration
- **Secure Storage**: Encrypted credentials
- **Auto-Logout**: Session validation on page access

### Dark Mode
- **System-Wide**: Toggle available in navigation
- **Persistent**: Saves user preference
- **Smooth Transitions**: Seamless theme switching

### Advanced Filtering
- Filter prompts by risk type (PII, PCI, PHI, INJECTION)
- Filter by decision (block, redact, warn, allow)
- Date range filtering
- Real-time search

## 🧪 Use Cases

### PII Detection
- Email addresses
- Social Security Numbers
- Phone numbers
- Credit card numbers
- IP addresses
- URLs
- Medical records

### Prompt Injection Prevention
- Instruction manipulation attempts
- Role-playing attacks
- Context injection
- Jailbreak attempts
- Data exfiltration

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t prompt-firewall .

# Run container
docker run -p 8000:8000 prompt-firewall
```

### Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/prompt-firewall
gcloud run deploy prompt-firewall \
  --image gcr.io/PROJECT_ID/prompt-firewall \
  --platform managed \
  --region us-central1
```

## 📈 Monitoring

### Metrics Tracked
- API response times
- Detection accuracy rates
- False positive/negative rates
- Tenant usage statistics
- Error rates

### Logging
- Structured JSON logs
- Complete audit trail
- Security event tracking
- Performance metrics

## 🔒 Security

### Features
- API key encryption
- bcrypt password hashing
- Tenant data isolation
- Rate limiting
- CORS protection
- Input validation
- Error sanitization

## 💰 Cost Estimation

**Monthly Costs (GCP)**
- Cloud Run: $10-20
- Firestore: $5-15
- Cloud Storage: $2-5
- Monitoring: $2-5
- **Total: ~$20-45/month**

## 📚 Documentation

- [Backend Architecture](backend/README_BACKEND_ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs) - Swagger UI
- [SDK Documentation](sdk/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License

---

**An enterprise-grade AI security platform protecting LLM applications from vulnerabilities.**
