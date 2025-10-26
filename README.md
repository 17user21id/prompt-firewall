# Prompt Firewall MVP - CloudMatos AI Security Engineer Take-Home Test

A comprehensive AI security firewall that detects PII/PHI and prompt injection attempts in real-time, with multi-tenant support and comprehensive audit logging.

## 🚀 Features

- **Multi-Tenant Architecture**: Isolated data and configurations per tenant
- **PII/PHI Detection**: Advanced pattern matching for emails, SSNs, phone numbers, credit cards
- **Prompt Injection Detection**: Heuristic and OpenAI-based detection methods
- **Policy Engine**: Configurable rules with versioning and priority management
- **Real-time Processing**: Fast API responses with comprehensive risk analysis
- **Audit Logging**: Complete audit trail for compliance and monitoring
- **Admin Console**: Web-based interface for management and monitoring
- **Python SDK**: Easy integration with existing applications
- **Serverless Deployment**: GCP Cloud Run with Firestore backend

## 📋 Requirements Met

### ✅ Core Requirements
- [x] User-facing demo UI
- [x] Admin console with authentication
- [x] Core firewall engine with PII/injection detection
- [x] API Gateway with RESTful endpoints
- [x] Python SDK with integration examples
- [x] Serverless cloud setup (GCP Cloud Run + Firestore)
- [x] Comprehensive logging and audit trail

### ✅ Bonus Features (+10 points)
- [x] Multi-tenant handling with isolated data
- [x] Policy versioning system
- [x] Anomaly scoring algorithms
- [x] Comprehensive statistics and monitoring

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
- **FastAPI**: Modern, fast web framework for building APIs
- **Google Cloud Firestore**: NoSQL database for multi-tenant data
- **Google Cloud Run**: Serverless container platform
- **Python 3.11**: Core runtime environment

### Frontend
- **Next.js 14**: React framework with App Router
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Modern UI components

### AI/ML
- **Custom PII Detection**: Regex-based pattern matching
- **Heuristic Injection Detection**: Keyword and pattern analysis
- **OpenAI Integration**: GPT-4 based injection detection (optional)

### Infrastructure
- **Terraform**: Infrastructure as Code
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline

## 📁 Project Structure

```
prompt-firewall/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── main.py           # FastAPI application
│   │   ├── firewall/         # Detection engine
│   │   │   ├── detector.py   # Main detector class
│   │   │   ├── rules.py      # Rules engine
│   │   │   └── injection_detection.py  # Provided detection code
│   │   ├── store/            # Data access layer
│   │   │   ├── base.py       # Abstract store interface
│   │   │   └── firestore/    # Firestore implementations
│   │   │       ├── tenants.py
│   │   │       ├── prompts.py
│   │   │       ├── rules.py
│   │   │       └── logs.py
│   │   ├── models/           # Pydantic models
│   │   │   └── schemas.py
│   │   ├── utils/            # Utilities
│   │   │   └── auth.py       # Authentication
│   │   └── tests/            # Test suite
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Container definition
│   └── config.env.example    # Environment configuration
├── frontend/                  # Next.js frontend
│   ├── pages/                # Page components
│   ├── components/           # Reusable components
│   └── styles/               # CSS styles
├── sdk/                      # Python SDK
│   ├── prompt_firewall/
│   │   ├── client.py         # SDK implementation
│   │   └── __init__.py
│   ├── setup.py              # Package configuration
│   └── README.md             # SDK documentation
├── terraform/                # Infrastructure as Code
│   ├── main.tf               # GCP resources
│   ├── variables.tf          # Variables
│   └── outputs.tf            # Outputs
└── docs/                     # Documentation
    ├── architecture.pdf      # Architecture diagram
    ├── threat_model.pdf      # Threat model
    └── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud SDK
- Docker (optional)

### 1. Backend Setup

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

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 3. SDK Usage

```bash
cd sdk

# Install SDK
pip install -e .

# Use in your application
python -c "
from prompt_firewall import PromptFirewallSDK
sdk = PromptFirewallSDK('http://localhost:8000', 'api-key', 'tenant-id')
result = sdk.query('My email is test@example.com')
print(f'Decision: {result[\"decision\"]}')
"
```

## 🔧 Configuration

### Environment Variables

```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# OpenAI (optional)
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4

# Security
JWT_SECRET=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]

# Features
ENABLE_OPENAI_DETECTION=false
ENABLE_RATE_LIMITING=true
```

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /tenants/{tenantId} {
      allow read, write: if request.auth != null && 
        request.auth.token.tenant_id == tenantId;
      match /{document=**} {
        allow read, write: if request.auth != null && 
          request.auth.token.tenant_id == tenantId;
      }
    }
  }
}
```

## 📊 API Endpoints

### Core Endpoints

- `POST /v1/tenants` - Create new tenant
- `POST /v1/query` - Process prompt through firewall
- `GET /v1/logs` - Retrieve audit logs
- `GET /v1/prompts` - Get prompt history
- `GET /v1/rules` - Manage detection rules

### Admin Endpoints

- `GET /v1/admin/tenants` - List all tenants
- `GET /v1/stats` - Comprehensive statistics
- `GET /health` - Health check

### SDK Integration

```python
from prompt_firewall import PromptFirewallSDK

# Initialize
sdk = PromptFirewallSDK(api_url, api_key, tenant_id)

# Process prompt
result = sdk.query("Contact me at john@example.com")
print(f"Decision: {result['decision']}")
print(f"Risks: {result['risks']}")

# Manage rules
rule = sdk.create_rule(
    rule_type="PII_EMAIL",
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    action="redact",
    severity="high"
)

# Get statistics
stats = sdk.get_stats()
print(f"Total prompts: {stats['prompt_stats']['total_prompts']}")
```

## 🧪 Testing

### Run Tests

```bash
cd backend
pytest tests/ -v --cov=src
```

### Test Scenarios Covered

- ✅ Valid inputs (normal questions)
- ✅ PII/PHI inputs (emails, SSNs, phone numbers)
- ✅ Prompt injection attempts
- ✅ Secret exfiltration attempts
- ✅ Large but clean prompts (scalability)
- ✅ Multi-tenant isolation
- ✅ Rule management
- ✅ Authentication and authorization

## 🚀 Deployment

### GCP Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/prompt-firewall
gcloud run deploy prompt-firewall \
  --image gcr.io/PROJECT_ID/prompt-firewall \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## 📈 Monitoring & Observability

### Metrics

- API response times
- Detection accuracy rates
- False positive/negative rates
- Tenant usage statistics
- Error rates and types

### Logging

- Structured JSON logs
- Complete audit trail
- Security event tracking
- Performance metrics

### Health Checks

- Database connectivity
- External API availability
- Service dependencies
- Resource utilization

## 🔒 Security Features

### Authentication & Authorization

- JWT-based authentication
- API key validation
- Tenant isolation
- Role-based access control

### Data Protection

- Encryption at rest and in transit
- PII detection and redaction
- Secure API key management
- Audit logging

### Threat Detection

- Prompt injection detection
- PII/PHI pattern matching
- Anomaly scoring
- Custom rule support

## 💰 Cost Estimation

### Monthly Costs (GCP)

- **Cloud Run**: $10-20 (moderate traffic)
- **Firestore**: $5-15 (based on reads/writes)
- **Cloud Storage**: $2-5 (logs and exports)
- **Cloud Monitoring**: $2-5 (metrics and alerts)
- **Total**: ~$20-45/month

### Optimization Strategies

- Efficient caching
- Batch operations
- Resource auto-scaling
- Cost monitoring alerts

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- [SDK Documentation](sdk/README.md) - Python SDK guide
- [Architecture Diagram](docs/architecture.pdf) - System design
- [Threat Model](docs/threat_model.pdf) - Security analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: [docs/](docs/)
- **Email**: support@cloudmatos.com

---

**Built for CloudMatos AI Security Engineer Take-Home Test**

*Demonstrating expertise in cybersecurity, AI security, cloud architecture, full-stack development, and serverless deployment.*
