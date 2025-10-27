#!/bin/bash

# Prompt Firewall - Start/Stop Services Script
# This script manages both backend and frontend services

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a process is running
is_running() {
    lsof -i:$1 >/dev/null 2>&1
}

# Function to stop a service
stop_service() {
    local port=$1
    local service_name=$2
    
    if is_running $port; then
        print_info "Stopping $service_name on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
        print_info "$service_name stopped successfully"
    else
        print_warning "$service_name is not running on port $port"
    fi
}

# Function to start backend
start_backend() {
    print_info "=== Setting up Backend ==="
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip (quietly)
    print_info "Upgrading pip..."
    pip install --upgrade pip -q
    
    # Check if dependencies need installation
    print_info "Checking backend dependencies..."
    if ! pip show fastapi > /dev/null 2>&1; then
        print_info "Installing backend dependencies (first time setup)..."
        pip install -r requirements.txt
    else
        print_info "Dependencies found. Skipping installation. Use 'pip install -r requirements.txt' to update."
    fi
    
    # Check if backend is already running
    if is_running 8000; then
        print_warning "Backend is already running on port 8000. Stopping it first..."
        stop_service 8000 "Backend"
    fi
    
    # Start backend in background
    print_info "Starting Backend on port 8000..."
    PYTHONPATH=src nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
    echo $! > ../logs/backend.pid
    
    cd ..
    
    # Wait and check if backend started successfully
    print_info "Waiting for backend to start..."
    sleep 5
    
    # Try multiple times to check if backend is running
    for i in {1..5}; do
        if is_running 8000; then
            print_info "✓ Backend is running on http://localhost:8000"
            break
        fi
        if [ $i -eq 5 ]; then
            print_error "Failed to start backend! Check logs/backend.log for details."
            exit 1
        fi
        sleep 2
    done
}

# Function to start frontend
start_frontend() {
    print_info "=== Setting up Frontend ==="
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_info "Installing frontend dependencies (first time setup)..."
        npm install
    else
        print_info "Dependencies found. Skipping installation. Use 'npm install' to update."
    fi
    
    # Check if frontend is already running
    if is_running 3000; then
        print_warning "Frontend is already running on port 3000. Stopping it first..."
        stop_service 3000 "Frontend"
    fi
    
    # Start frontend in background
    print_info "Starting Frontend on port 3000..."
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/frontend.pid
    
    cd ..
    
    # Wait and check if frontend started successfully
    print_info "Waiting for frontend to start..."
    sleep 8
    
    # Try multiple times to check if frontend is running
    for i in {1..5}; do
        if is_running 3000; then
            print_info "✓ Frontend is running on http://localhost:3000"
            break
        fi
        if [ $i -eq 5 ]; then
            print_error "Failed to start frontend! Check logs/frontend.log for details."
            exit 1
        fi
        sleep 2
    done
}

# Function to stop both services
stop_services() {
    print_info "=== Stopping Services ==="
    
    # Stop backend
    if [ -f "logs/backend.pid" ]; then
        PID=$(cat logs/backend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_info "Stopping backend (PID: $PID)..."
            kill $PID 2>/dev/null || true
            rm logs/backend.pid
        fi
    fi
    stop_service 8000 "Backend"
    
    # Stop frontend
    if [ -f "logs/frontend.pid" ]; then
        PID=$(cat logs/frontend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_info "Stopping frontend (PID: $PID)..."
            kill $PID 2>/dev/null || true
            rm logs/frontend.pid
        fi
    fi
    stop_service 3000 "Frontend"
    
    print_info "✓ All services stopped"
}

# Function to check service status
status() {
    print_info "=== Service Status ==="
    
    if is_running 8000; then
        print_info "✓ Backend is running on port 8000"
    else
        print_warning "✗ Backend is not running"
    fi
    
    if is_running 3000; then
        print_info "✓ Frontend is running on port 3000"
    else
        print_warning "✗ Frontend is not running"
    fi
}

# Main script logic
main() {
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    case "${1:-start}" in
        start)
            print_info "Starting Prompt Firewall services..."
            print_info "======================================"
            
            # Stop any existing services first
            print_info "Stopping any existing services..."
            stop_services
            sleep 2
            
            # Start backend
            start_backend
            
            # Wait a bit before starting frontend
            sleep 2
            
            # Start frontend
            start_frontend
            
            print_info ""
            print_info "======================================"
            print_info "✓ All services started successfully!"
            print_info ""
            print_info "Backend API: http://localhost:8000"
            print_info "Backend Docs: http://localhost:8000/docs"
            print_info "Frontend: http://localhost:3000"
            print_info ""
            print_info "To stop services, run: ./start_services.sh stop"
            print_info "To check status, run: ./start_services.sh status"
            ;;
        
        stop)
            stop_services
            ;;
        
        status)
            status
            ;;
        
        restart)
            print_info "Restarting services..."
            stop_services
            sleep 2
            $0 start
            ;;
        
        *)
            echo "Usage: $0 {start|stop|status|restart}"
            echo ""
            echo "Commands:"
            echo "  start   - Start both backend and frontend services"
            echo "  stop    - Stop both backend and frontend services"
            echo "  status  - Check status of services"
            echo "  restart - Restart both services"
            exit 1
            ;;
    esac
}

main "$@"

