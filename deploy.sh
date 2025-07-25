#!/bin/bash

# Shoulder Distance API Deployment Script
# This script deploys the streaming API with nginx for global access

set -e

echo "🚀 Deploying Shoulder Distance Streaming API..."

# Check if running as root for nginx setup
if [[ $EUID -eq 0 ]]; then
   echo "⚠️ Running as root. This is required for nginx setup."
else
   echo "ℹ️ Running as non-root user. Some nginx operations may require sudo."
fi

# Function to install dependencies on different systems
install_dependencies() {
    echo "📦 Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y nginx curl python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y nginx curl python3-pip python3-venv
    elif command -v brew &> /dev/null; then
        # macOS
        brew install nginx curl
    else
        echo "⚠️ Unsupported package manager. Please install nginx and curl manually."
    fi
}

# Function to setup Python environment
setup_python_env() {
    echo "🐍 Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install Python dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Python environment ready"
}

# Function to setup nginx
setup_nginx() {
    echo "🌐 Setting up nginx configuration..."
    
    # Backup existing nginx config
    if [ -f "/etc/nginx/nginx.conf" ]; then
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)
        echo "📋 Backed up existing nginx config"
    fi
    
    # Copy our nginx config
    sudo cp nginx.conf /etc/nginx/nginx.conf
    
    # Test nginx configuration
    sudo nginx -t
    
    # Create log directory if it doesn't exist
    sudo mkdir -p /var/log/nginx
    
    echo "✅ Nginx configured"
}

# Function to start services
start_services() {
    echo "🎬 Starting services..."
    
    # Start nginx
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable nginx
        sudo systemctl restart nginx
        echo "✅ Nginx started"
    else
        sudo nginx -s reload || sudo nginx
        echo "✅ Nginx reloaded"
    fi
    
    # Start the Python API in background
    echo "🚀 Starting Shoulder Distance API..."
    source venv/bin/activate
    
    # Kill any existing processes on port 5000
    sudo lsof -ti:5000 | xargs sudo kill -9 2>/dev/null || true
    
    # Start the API
    nohup python streaming_api.py > api.log 2>&1 &
    API_PID=$!
    
    echo "🎯 API started with PID: $API_PID"
    echo "📝 Logs are being written to api.log"
    
    # Wait a moment for the API to start
    sleep 3
    
    # Check if API is responding
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ API health check passed"
    else
        echo "❌ API health check failed"
        echo "📝 Check api.log for errors"
    fi
}

# Function to check firewall
check_firewall() {
    echo "🔥 Checking firewall settings..."
    
    if command -v ufw &> /dev/null; then
        # Ubuntu UFW
        sudo ufw allow 80
        sudo ufw allow 8080
        sudo ufw allow 443
        echo "✅ UFW firewall rules added"
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewalld
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=8080/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --reload
        echo "✅ Firewalld rules added"
    else
        echo "⚠️ No recognized firewall. Make sure ports 80, 8080, 443 are open"
    fi
}

# Function to display final information
show_endpoints() {
    echo ""
    echo "🎉 Deployment Complete!"
    echo "=" * 50
    echo ""
    echo "📡 Your Shoulder Distance API is now accessible at:"
    echo "   🌐 Web Interface: http://$(hostname -I | awk '{print $1}'):8080"
    echo "   🌐 Web Interface (local): http://localhost:8080"
    echo "   📡 WebSocket: ws://$(hostname -I | awk '{print $1}'):8080/socket.io/"
    echo "   🔧 REST API: http://$(hostname -I | awk '{print $1}'):8080/process_image"
    echo "   ❤️ Health Check: http://$(hostname -I | awk '{print $1}'):8080/health"
    echo ""
    echo "🔧 API Features:"
    echo "   ✅ Real-time video streaming with pose detection"
    echo "   ✅ Shoulder and waist measurements in cm"
    echo "   ✅ WebSocket support for live streaming"
    echo "   ✅ REST API for single image processing"
    echo "   ✅ Automatic calibration (650px = 96cm)"
    echo "   ✅ 3D depth information"
    echo ""
    echo "📝 Management Commands:"
    echo "   🔄 Restart API: sudo pkill -f streaming_api.py && nohup python streaming_api.py > api.log 2>&1 &"
    echo "   🔄 Restart Nginx: sudo systemctl restart nginx"
    echo "   📊 Check API logs: tail -f api.log"
    echo "   📊 Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
    echo "   🛑 Stop API: sudo pkill -f streaming_api.py"
    echo ""
    echo "🌍 For global access, configure your router/firewall to forward ports 80, 8080, 443"
    echo "🔒 For production, add SSL certificates to the ssl/ directory"
}

# Main deployment process
main() {
    echo "🎯 Shoulder Distance API Global Deployment"
    echo "========================================"
    
    # Check if we're in the right directory
    if [ ! -f "streaming_api.py" ]; then
        echo "❌ streaming_api.py not found. Please run this script from the project directory."
        exit 1
    fi
    
    # Ask for confirmation
    read -p "🤔 This will install nginx and deploy the API globally. Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
    
    # Run deployment steps
    install_dependencies
    setup_python_env
    setup_nginx
    check_firewall
    start_services
    show_endpoints
    
    echo "🚀 Deployment completed successfully!"
}

# Handle script termination
cleanup() {
    echo "🧹 Cleaning up..."
    # Add any cleanup commands here
}
trap cleanup EXIT

# Run main function
main "$@" 