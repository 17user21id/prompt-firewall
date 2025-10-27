#!/bin/bash

# Prompt Firewall - Stop Services Script
# This script stops both backend and frontend services

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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
        
        # Check if actually stopped
        if is_running $port; then
            print_error "Failed to stop $service_name"
            return 1
        else
            print_info "$service_name stopped successfully"
            return 0
        fi
    else
        print_warning "$service_name is not running on port $port"
        return 0
    fi
}

# Main function to stop all services
stop_all_services() {
    print_info "Stopping Prompt Firewall services..."
    print_info "======================================"
    
    # Stop backend
    print_info ""
    print_info "Stopping Backend..."
    if [ -f "logs/backend.pid" ]; then
        PID=$(cat logs/backend.pid 2>/dev/null || echo "")
        if [ ! -z "$PID" ] && ps -p $PID > /dev/null 2>&1; then
            print_info "Stopping backend process (PID: $PID)..."
            kill $PID 2>/dev/null || true
            rm logs/backend.pid 2>/dev/null || true
            sleep 1
        fi
    fi
    stop_service 8000 "Backend"
    
    # Stop frontend
    print_info ""
    print_info "Stopping Frontend..."
    if [ -f "logs/frontend.pid" ]; then
        PID=$(cat logs/frontend.pid 2>/dev/null || echo "")
        if [ ! -z "$PID" ] && ps -p $PID > /dev/null 2>&1; then
            print_info "Stopping frontend process (PID: $PID)..."
            kill $PID 2>/dev/null || true
            rm logs/frontend.pid 2>/dev/null || true
            sleep 1
        fi
    fi
    stop_service 3000 "Frontend"
    
    # Clean up any remaining processes on those ports
    print_info ""
    print_info "Cleaning up any remaining processes..."
    
    # Kill any remaining processes on port 8000
    if is_running 8000; then
        print_warning "Force killing remaining processes on port 8000..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill any remaining processes on port 3000
    if is_running 3000; then
        print_warning "Force killing remaining processes on port 3000..."
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    fi
    
    print_info ""
    print_info "======================================"
    print_info "✓ All services stopped"
    
    # Verify ports are free
    print_info ""
    print_info "Verifying ports are free..."
    if ! is_running 8000 && ! is_running 3000; then
        print_info "✓ All ports (8000, 3000) are now free"
    else
        print_warning "Some ports may still be in use. Check manually:"
        [ "$(is_running 8000 && echo 'yes')" = "yes" ] && print_warning "  - Port 8000 is still in use"
        [ "$(is_running 3000 && echo 'yes')" = "yes" ] && print_warning "  - Port 3000 is still in use"
    fi
}

# Check if we should force stop
FORCE_STOP=false
if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
    FORCE_STOP=true
fi

# Run the stop function
stop_all_services

# If force stop is enabled, do an extra aggressive cleanup
if [ "$FORCE_STOP" = "true" ]; then
    print_info ""
    print_info "Performing force cleanup..."
    
    # Try to find and kill any uvicorn processes
    UPLIST=$(pgrep -f "uvicorn.*src.main:app" 2>/dev/null || echo "")
    if [ ! -z "$UPLIST" ]; then
        print_info "Killing uvicorn processes: $UPLIST"
        kill -9 $UPLIST 2>/dev/null || true
    fi
    
    # Try to find and kill any next dev processes
    NEXTLIST=$(pgrep -f "next dev" 2>/dev/null || echo "")
    if [ ! -z "$NEXTLIST" ]; then
        print_info "Killing next dev processes: $NEXTLIST"
        kill -9 $NEXTLIST 2>/dev/null || true
    fi
    
    print_info "✓ Force cleanup complete"
fi

print_info ""
print_info "Done!"

