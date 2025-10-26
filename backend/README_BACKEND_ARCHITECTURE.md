# Prompt Firewall Backend - Architecture & API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Core Components](#core-components)
5. [API Endpoints](#api-endpoints)
6. [Request/Response Schema](#requestresponse-schema)
7. [Database Schema](#database-schema)
8. [Security](#security)
9. [Development](#development)

---

## Overview

Prompt Firewall is an AI security system designed to protect Large Language Model (LLM) applications from prompt injection attacks and prevent Personally Identifiable Information (PII) leakage. The backend is built using **FastAPI**, **Firestore**, and provides a comprehensive multi-tenant architecture.

### Key Features
- **Multi-tenant Architecture**: Isolated tenant data with API key authentication
- **PII Detection**: Regex-based detection of emails, SSNs, phones, credit cards, IPs, etc.
- **Prompt Injection Detection**: Heuristic-based and OpenAI-powered injection detection
- **Custom Rules Engine**: Tenant-specific security rules
- **Comprehensive Logging**: Audit trail for all security events
- **Rate Limiting**: API request throttling
- **OpenAPI Documentation**: Auto-generated API docs

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client (Frontend/SDK)                       │
└────────────────────────────┬────────────────────────────────────────┘
                              │
                              │ HTTPS/REST API
                              │
┌─────────────────────────────▼──────────────────────────────────────┐
│                      FastAPI Application                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  API Layer (api/)                            │  │
│  │  ┌──────────┐ ┌─────────┐ ┌──────┐ ┌───────┐ ┌──────────┐ │  │
│  │  │  Health  │ │ Tenants │ │Query │ │Rules │ │  Logs    │ │  │
│  │  └──────────┘ └─────────┘ └──────┘ └──────┘ └──────────┘ │  │
│  └───────────────┬───────────────────────────────────────────┘  │
│                  │                                           │  │
│  ┌───────────────▼───────────────────────────────────────────┐  │
│  │            Business Logic Layer                          │  │
│  │  ┌───────────────────────────────────────────────────┐  │  │
│  │  │              Authentication (auth.py)             │  │  │
│  │  │  - API Key Validation                              │  │  │
│  │  │  - Password Hashing (bcrypt)                        │  │  │
│  │  │  - Token Encryption (Fernet)                      │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  │  ┌───────────────────────────────────────────────────┐  │  │
│  │  │         Firewall Detection (firewall/)            │  │  │
│  │  │  - FirewallDetector (regex-based PII)            │  │  │
│  │  │  - OpenAIFirewallDetector (AI-based)              │  │  │
│  │  │  - HybridFirewallDetector (combined)               │  │  │
│  │  │  - Injection Detection                            │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  │  ┌───────────────────────────────────────────────────┐  │  │
│  │  │         Rules Engine (firewall/rules.py)          │  │  │
│  │  │  - Rule Application                                │  │  │
│  │  │  - Action Enforcement (block/redact/warn)        │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  └───────────────┬───────────────────────────────────────────┘  │
│                  │                                           │  │
│  ┌───────────────▼───────────────────────────────────────────┐  │
│  │         Data Access Layer (store/)                       │  │
│  │  ┌──────────┐ ┌─────────┐ ┌──────┐ ┌──────┐ ┌────────┐ │  │
│  │  │  Tenants │ │ Prompts  │ │Rules │ │ Logs │ │ Abstract│ │  │
│  │  │  Store   │ │  Store   │ │ Store│ │ Store│ │  Store  │ │  │
│  │  └──────────┘ └─────────┘ └──────┘ └──────┘ └────────┘ │  │
│  └───────────────┬───────────────────────────────────────────┘  │
└──────────────────┼───────────────────────────────────────────────┘
                   │
                   │ Firestore API
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                Google Cloud Firestore                       │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Collection: tenants                                   │ │
│  │  Collection: prompts/{tenant_id}/prompts              │ │
│  │  Collection: rules/{tenant_id}/rules                  │ │
│  │  Collection: logs/{tenant_id}/logs                    │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Flow of Request Processing

1. **Request Arrives**: Client sends API request with authentication
2. **Authentication**: `get_current_tenant()` validates Bearer token (tenant_id:api_key)
3. **Rate Limiting**: `check_rate_limit()` prevents API abuse
4. **Data Retrieval**: Fetch tenant-specific rules from Firestore
5. **Detection**: FirewallDetector analyzes the prompt
6. **Rule Application**: RulesEngine applies custom rules
7. **Decision**: Block/Redact/Warn/Allow based on findings
8. **Storage**: Save prompt and log to Firestore
9. **Response**: Return analysis results to client

---

## Directory Structure

```
backend/
├── src/
│   ├── api/                      # API endpoint handlers
│   │   ├── health.py             # Health check endpoints
│   │   ├── tenants.py            # Tenant management endpoints
│   │   ├── query.py              # Prompt processing endpoints
│   │   ├── rules.py              # Rule management endpoints
│   │   ├── logs.py               # Log query endpoints
│   │   ├── prompts.py            # Prompt history endpoints
│   │   ├── admin.py              # Admin endpoints
│   │   └── routers.py            # Router aggregation
│   │
│   ├── common/                    # Shared utilities
│   │   ├── auth.py               # Authentication & authorization
│   │   ├── logger.py             # Logging configuration
│   │   ├── firestore_config.py   # Firestore connection
│   │   ├── config_constants.py   # Configuration constants
│   │   ├── api_constants.py      # API response constants
│   │   ├── auth_constants.py     # Authentication constants
│   │   ├── database_constants.py # Database constants
│   │   ├── firewall_constants.py # Firewall constants
│   │   ├── logging_constants.py  # Logging constants
│   │   ├── message_templates.py # Error message templates
│   │   ├── regex_constants.py    # Regex patterns
│   │   └── security_constants.py # Security constants
│   │
│   ├── firewall/                 # Detection engine
│   │   ├── detector.py           # Main FirewallDetector
│   │   ├── hybrid_detector.py    # Hybrid detection (regex + AI)
│   │   ├── injection_detection.py # Injection detection logic
│   │   ├── openai_detector.py   # OpenAI-powered detection
│   │   ├── rules.py              # RulesEngine for applying rules
│   │   └── templates.py          # Detection templates
│   │
│   ├── models/                    # Pydantic models
│   │   └── schemas.py            # Request/Response schemas
│   │
│   ├── store/                     # Data access layer
│   │   ├── base.py               # Abstract store interface
│   │   └── firestore/            # Firestore implementations
│   │       ├── base.py           # Base Firestore store
│   │       ├── tenants.py        # TenantStore
│   │       ├── prompts.py        # PromptStore
│   │       ├── rules.py          # RuleStore
│   │       └── logs.py           # LogStore
│   │
│   └── main.py                    # FastAPI application entry point
│
├── tests/                         # Test files
├── logs/                          # Application logs
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
├── config.env.example            # Environment variable template
├── service-account-key.json      # Google Cloud credentials (not in git)
└── README.md                      # Backend documentation
```

---

## Core Components

### 1. API Layer (`api/`)

FastAPI route handlers for all endpoints.

#### Key Files:
- **`health.py`**: `/health` endpoint for system status
- **`tenants.py`**: `/v1/tenants` - Tenant CRUD operations
- **`query.py`**: `/v1/query` - Prompt processing
- **`rules.py`**: `/v1/rules` - Rule management
- **`logs.py`**: `/v1/logs` - Log queries
- **`admin.py`**: `/v1/admin` - Admin operations

### 2. Authentication (`common/auth.py`)

#### Features:
- **bcrypt**: Password hashing
- **Fernet**: API key encryption
- **HTTPBearer**: Bearer token validation
- **Rate Limiting**: Request throttling per tenant

#### Key Functions:
```python
def get_current_tenant(credentials: HTTPAuthorizationCredentials) -> str
    """Extract and validate tenant from Bearer token."""
    
def check_rate_limit(tenant_id: str)
    """Enforce rate limiting per tenant."""
```

### 3. Firewall Detection (`firewall/`)

#### FirewallDetector (`detector.py`)
- **Regex-based PII Detection**: Email, SSN, phone, credit card, IP address, URL, medical records
- **Heuristic Injection Detection**: Pattern-based injection detection
- **OpenAI Integration**: AI-powered detection (optional)

#### Detection Methods:
1. **PII Detection**: Regex patterns for sensitive data
2. **Prompt Injection**: Heuristic scoring based on suspicious patterns
3. **Anomaly Scoring**: Calculates risk scores (0.0 - 1.0)
4. **Custom Rules**: Tenant-specific detection rules

### 4. Rules Engine (`firewall/rules.py`)

#### Actions:
- **BLOCK**: Completely reject the request
- **REDACT**: Remove sensitive content before processing
- **WARN**: Allow but log warning
- **ALLOW**: Process normally

### 5. Data Access Layer (`store/`)

#### Abstract Store Interface:
```python
class Store(ABC):
    def save(tenant_id: str, data: Dict) -> str
    def get(tenant_id: str, record_id: str) -> Optional[Dict]
    def query(tenant_id: str, filters: Dict) -> List[Dict]
    def update(tenant_id: str, record_id: str, data: Dict) -> bool
    def delete(tenant_id: str, record_id: str) -> bool
```

#### Firestore Stores:
- **TenantStore**: Tenant management
- **PromptStore**: Prompt history
- **RuleStore**: Custom rules
- **LogStore**: Event logs

---

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Authentication
All endpoints (except `/health`) require Bearer token authentication:
```
Authorization: Bearer <tenant_id>:<api_key>
```

### Endpoints

#### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "services": {
    "firestore": "connected",
    "cache": "active"
  }
}
```

#### 2. Tenant Management

##### Create Tenant
```http
POST /v1/tenants
Content-Type: application/json

{
  "name": "Acme Corp",
  "password": "secure_password_123",
  "metadata": {}
}
```

**Response:**
```json
{
  "tenant_id": "abc123...",
  "name": "Acme Corp",
  "api_key": "encrypted_key...",
  "created_at": "2024-01-01T00:00:00Z",
  "status": "active"
}
```

##### Login
```http
POST /v1/tenants/login
Content-Type: application/json

{
  "name": "Acme Corp",
  "password": "secure_password_123"
}
```

**Response:**
```json
{
  "tenant_id": "abc123...",
  "name": "Acme Corp",
  "api_key": "encrypted_key...",
  "message": "Login successful",
  "status": "success"
}
```

#### 3. Query Processing

##### Process Prompt
```http
POST /v1/query
Authorization: Bearer abc123:api_key_here
Content-Type: application/json

{
  "tenant_id": "abc123",
  "prompt": "User email: john@example.com",
  "user_id": "user_123",
  "metadata": {}
}
```

**Response:**
```json
{
  "decision": "redact",
  "promptModified": "User email: [REDACTED]",
  "risks": [
    {
      "type": "PII_EMAIL",
      "match": "john@example.com",
      "severity": "high",
      "action": "redact",
      "confidence": 0.95
    }
  ],
  "prompt_id": "prompt_123",
  "timestamp": "2024-01-01T00:00:00Z",
  "anomaly_score": 0.75,
  "confidence": 0.95,
  "reason": "PII detected in input",
  "applied_rules": ["rule_001", "rule_002"]
}
```

#### 4. Rules Management

##### Create Rule
```http
POST /v1/rules
Authorization: Bearer tenant_id:api_key
Content-Type: application/json

{
  "type": "PII_EMAIL",
  "pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
  "action": "redact",
  "severity": "high",
  "description": "Email detection rule",
  "enabled": true
}
```

##### List Rules
```http
GET /v1/rules?tenant_id=abc123&limit=100
Authorization: Bearer tenant_id:api_key
```

##### Update Rule
```http
PUT /v1/rules/{rule_id}
Authorization: Bearer tenant_id:api_key
Content-Type: application/json

{
  "action": "block",
  "enabled": true
}
```

#### 5. Logs

##### Query Logs
```http
GET /v1/logs?tenant_id=abc123&limit=100&date_from=2024-01-01
Authorization: Bearer tenant_id:api_key
```

**Response:**
```json
{
  "logs": [
    {
      "log_id": "log_123",
      "prompt_id": "prompt_123",
      "event_type": "processed",
      "details": {
        "decision": "redact",
        "risks_detected": 1
      },
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### 6. Admin

##### Get Statistics
```http
GET /v1/admin/stats?tenant_id=abc123
Authorization: Bearer tenant_id:api_key
```

---

## Request/Response Schema

### Enums

#### SeverityLevel
```python
LOW = "low"
MEDIUM = "medium"
HIGH = "high"
```

#### ActionType
```python
BLOCK = "block"    # Reject the request
REDACT = "redact"  # Remove sensitive content
WARN = "warn"      # Allow but log warning
ALLOW = "allow"    # Process normally
```

#### RiskType
```python
PII_EMAIL = "PII_EMAIL"
PII_SSN = "PII_SSN"
PII_PHONE = "PII_PHONE"
PII_CREDIT_CARD = "PII_CREDIT_CARD"
PII_IP_ADDRESS = "PII_IP_ADDRESS"
PII_URL = "PII_URL"
PII_MEDICAL_RECORD = "PII_MEDICAL_RECORD"
INJECTION = "INJECTION"
INJECTION_OPENAI = "INJECTION_OPENAI"
CUSTOM = "CUSTOM"
```

### Core Models

#### QueryRequest
```python
{
  "tenant_id": str,      # Required
  "prompt": str,          # Required, 1-10000 chars
  "user_id": str,         # Optional
  "metadata": dict        # Optional
}
```

#### QueryResponse
```python
{
  "decision": ActionType,              # BLOCK, REDACT, WARN, or ALLOW
  "promptModified": str,                # Modified prompt after redaction
  "risks": List[Risk],                  # Detected risks
  "prompt_id": str,                     # Unique prompt ID
  "timestamp": str,                      # ISO 8601 timestamp
  "anomaly_score": float,               # 0.0 - 1.0
  "confidence": float,                  # 0.0 - 1.0
  "reason": str,                        # Explanation
  "applied_rules": List[Dict]           # Applied rules
}
```

#### Risk
```python
{
  "type": RiskType,          # Type of risk detected
  "match": str,              # Matched text
  "start": int,              # Optional: Start position
  "end": int,               # Optional: End position
  "severity": SeverityLevel, # LOW, MEDIUM, or HIGH
  "action": ActionType,      # BLOCK, REDACT, WARN, or ALLOW
  "confidence": float,      # 0.0 - 1.0
  "score": float,           # Optional: Calculated score
  "reasoning": str,         # Optional: AI reasoning
  "rule_id": str           # Optional: Applied rule ID
}
```

#### RuleResponse
```python
{
  "rule_id": str,              # Unique rule ID
  "type": str,                 # Rule type (PII_EMAIL, etc.)
  "pattern": str,              # Regex pattern
  "action": ActionType,        # BLOCK, REDACT, WARN, or ALLOW
  "severity": SeverityLevel,   # LOW, MEDIUM, or HIGH
  "version": int,              # Rule version
  "created_at": str,          # ISO 8601 timestamp
  "updated_at": str,           # ISO 8601 timestamp
  "enabled": bool,            # Active flag
  "description": str,          # Rule description
  "metadata": dict            # Additional metadata
}
```

---

## Database Schema

### Firestore Collections

#### `tenants` Collection
```json
{
  "tenant_id": "abc123...",
  "name": "Acme Corp",
  "password_hash": "bcrypt_hash...",
  "api_key": "encrypted_key...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "status": "active",
  "metadata": {}
}
```

#### `prompts/{tenant_id}/prompts` Collection
```json
{
  "prompt_id": "prompt_123...",
  "prompt": "Original prompt text",
  "response": "AI response",
  "decision": "redact",
  "promptModified": "Modified prompt",
  "risks": [...],
  "anomaly_score": 0.75,
  "timestamp": "2024-01-01T00:00:00Z",
  "user_id": "user_123",
  "metadata": {}
}
```

#### `rules/{tenant_id}/rules` Collection
```json
{
  "rule_id": "rule_123...",
  "type": "PII_EMAIL",
  "pattern": "[a-zA-Z0-9._%+-]+@...",
  "action": "redact",
  "severity": "high",
  "version": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "enabled": true,
  "description": "Email detection",
  "metadata": {}
}
```

#### `logs/{tenant_id}/logs` Collection
```json
{
  "log_id": "log_123...",
  "prompt_id": "prompt_123...",
  "event_type": "processed",
  "details": {
    "decision": "redact",
    "risks_detected": 1
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "user_id": "user_123",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "metadata": {}
}
```

---

## Security

### Authentication & Authorization

1. **API Key Authentication**:
   - Format: `Bearer <tenant_id>:<api_key>`
   - Validated using HTTPBearer security scheme
   - Keys encrypted using Fernet (symmetric encryption)

2. **Password Security**:
   - Hashed using bcrypt with salt
   - Minimum 8 characters required
   - Not stored in plain text

3. **Rate Limiting**:
   - Per-tenant request throttling
   - Prevents API abuse
   - Configurable limits

4. **Tenant Isolation**:
   - Data segregated by `tenant_id`
   - Firestore security rules enforce isolation
   - API validates tenant ownership

### Detection Capabilities

#### PII Detection Patterns
- **Email**: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- **SSN**: `\b\d{3}-\d{2}-\d{4}\b`
- **Phone**: `\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b`
- **Credit Card**: `\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b`
- **IP Address**: `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b`
- **URL**: `https?://[^\s]+`
- **Medical Record**: Keywords like patient, medical, diagnosis, etc.

#### Prompt Injection Detection
- Heuristic scoring based on suspicious patterns
- OpenAI-powered detection (optional)
- Anomaly scoring (0.0 - 1.0)

---

## Development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config.env.example .env
# Edit .env with your credentials

# Add Firestore credentials
# Place service-account-key.json in backend/ directory

# Run the application
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

```bash
# OpenAI (optional)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Firestore
GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
FIRESTORE_PROJECT_ID=prompt-firewall-mvp

# Application
PORT=8000
ENVIRONMENT=development
DEBUG=true

# Encryption
ENCRYPTION_KEY=...  # Fernet encryption key
```

### Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=backend --cov-report=html
```

### Docker

```bash
# Build image
docker build -t prompt-firewall-backend .

# Run container
docker run -p 8000:8000 prompt-firewall-backend
```

### API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Key Technologies

- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation using Python type annotations
- **Firestore**: NoSQL database (Google Cloud)
- **bcrypt**: Password hashing
- **Fernet**: Symmetric encryption (API keys)
- **OpenAI**: AI-powered detection (optional)
- **uvicorn**: ASGI server

---

## License

Copyright © 2024 Prompt Firewall MVP. All rights reserved.

