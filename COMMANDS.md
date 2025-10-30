# Prompt Firewall - Quick Command Reference

## Start Services

### Start All Services (Backend + Frontend)
```bash
./start_services.sh start
```

### Start Backend Only
```bash
cd backend && source venv/bin/activate && PYTHONPATH=src uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Start Frontend Only
```bash
cd frontend && npm run dev
```

### Stop All Services
```bash
./start_services.sh stop
```

### Check Service Status
```bash
./start_services.sh status
```

---

## Run Tests

### Run All Tests
```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/ -v
```

### Run Specific Test File
```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_firewall_comprehensive.py -v
```

### Run Tests with Coverage
```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/ -v --cov=src --cov-report=html
```

### Run Tests and Show Output
```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/ -v -s
```

---

## Useful Development Commands

### Activate Backend Virtual Environment
```bash
cd backend && source venv/bin/activate
```

### Install Backend Dependencies
```bash
cd backend && source venv/bin/activate && pip install -r requirements.txt
```

### Install Frontend Dependencies
```bash
cd frontend && npm install
```

### Check Backend Logs
```bash
tail -f logs/backend.log
```

### Check Frontend Logs
```bash
tail -f logs/frontend.log
```

---

## Service URLs

- **Backend API**: http://localhost:8000
- **Backend API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

