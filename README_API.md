# 🎯 Shoulder Distance Streaming API

A real-time body measurement API that processes live video streams and provides shoulder and waist measurements using MediaPipe pose detection.

## 🌟 Features

- **🎥 Real-time video streaming** with WebSocket support
- **📏 Accurate measurements** in centimeters and pixels
- **🎯 Pose detection** using MediaPipe with confidence scoring
- **🌐 Global access** via nginx reverse proxy
- **🔧 REST API** for single image processing
- **📊 3D depth information** and posture analysis
- **⚙️ Automatic calibration** (650px = 96cm default)
- **🖥️ Web interface** for easy testing and interaction

## 🚀 Quick Start

### Option 1: Automatic Deployment (Recommended)

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

This will automatically:
- Install system dependencies (nginx, python3, etc.)
- Set up Python virtual environment
- Configure nginx for global access
- Start all services
- Configure firewall rules

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   # Install streaming requirements
   pip install -r streaming_requirements.txt
   
   # Install nginx (Ubuntu/Debian)
   sudo apt-get install nginx
   ```

2. **Start the API**
   ```bash
   python streaming_api.py
   ```

3. **Configure Nginx** (Optional for global access)
   ```bash
   sudo cp nginx.conf /etc/nginx/nginx.conf
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Option 3: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

## 🌐 Access Points

After deployment, your API will be accessible at:

- **🌐 Web Interface**: `http://YOUR_IP:8080`
- **📡 WebSocket**: `ws://YOUR_IP:8080/socket.io/`
- **🔧 REST API**: `http://YOUR_IP:8080/process_image`
- **❤️ Health Check**: `http://YOUR_IP:8080/health`

## 📡 API Usage

### WebSocket Real-time Streaming

```javascript
const socket = io('ws://YOUR_IP:8080');

// Send frame for processing
socket.emit('process_frame', {
    frame: base64EncodedImage
});

// Receive processed results
socket.on('processed_frame', (data) => {
    console.log('Measurements:', data.measurements);
    displayImage(data.frame); // base64 encoded processed image
});

// Control calibration
socket.emit('calibrate', { preset: true }); // Use 650px = 96cm
socket.emit('toggle_z_info'); // Toggle depth information
```

### REST API

```bash
# Process single image
curl -X POST \
  http://YOUR_IP:8080/process_image \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@your_image.jpg'

# Health check
curl http://YOUR_IP:8080/health

# Get status
curl http://YOUR_IP:8080/status
```

### Python Client Example

```python
import requests
import json

# Process image via REST API
with open('test_image.jpg', 'rb') as f:
    response = requests.post(
        'http://YOUR_IP:8080/process_image',
        files={'image': f}
    )

result = response.json()
print(f"Shoulder: {result['measurements']['shoulder_cm']:.1f} cm")
print(f"Waist: {result['measurements']['waist_cm']:.1f} cm")
```

## 📊 Response Format

### Measurement Data Structure

```json
{
  "measurements": {
    "shoulder_3d": 0.234,
    "shoulder_pixels": 145.2,
    "shoulder_cm": 21.4,
    "waist_3d": 0.198,
    "waist_pixels": 122.8,
    "waist_cm": 18.1,
    "confidence": 0.97,
    "fps": 15.2,
    "frame_count": 1247,
    "scale_info": "User calibration: 6.77 px/cm (650px=96cm)",
    "z_info": {
      "shoulder_left_z": -0.123,
      "shoulder_right_z": -0.118,
      "shoulder_z_diff": 0.005,
      "waist_left_z": -0.089,
      "waist_right_z": -0.091,
      "waist_z_diff": 0.002,
      "shoulder_depth_cm": 8.3,
      "waist_depth_cm": 6.1
    },
    "timestamp": 1672531200.123
  },
  "processed_image": "base64_encoded_image_with_overlays"
}
```

## ⚙️ Configuration

### Calibration Options

1. **Default Calibration**: 650px = 96cm (automatically active)
2. **Manual Calibration**: Use reference objects via web interface
3. **API Calibration**: Send custom calibration via WebSocket

### Environment Variables

```bash
# Set in your environment or docker-compose.yml
FLASK_ENV=production          # production/development
API_HOST=0.0.0.0             # Host to bind to
API_PORT=5000                # Port to run on
MAX_UPLOAD_SIZE=50MB         # Maximum image upload size
```

### Nginx Configuration

The nginx configuration includes:
- **Rate limiting**: 10 req/s for API, 30 req/s for streaming
- **CORS headers**: Full cross-origin support
- **WebSocket upgrade**: Automatic Socket.IO support
- **Security headers**: XSS protection, content security policy
- **File upload**: 50MB limit for image processing

## 🔒 Security Features

- **Rate limiting** to prevent abuse
- **CORS protection** with configurable origins
- **Security headers** (XSS, CSRF, etc.)
- **Input validation** for all uploads
- **Non-root container** execution
- **Health checks** and monitoring

## 🚨 Troubleshooting

### Common Issues

1. **API not responding**
   ```bash
   # Check if API is running
   ps aux | grep streaming_api.py
   
   # Check logs
   tail -f api.log
   
   # Restart API
   sudo pkill -f streaming_api.py
   nohup python streaming_api.py > api.log 2>&1 &
   ```

2. **Nginx errors**
   ```bash
   # Check nginx status
   sudo systemctl status nginx
   
   # Check nginx logs
   sudo tail -f /var/log/nginx/error.log
   
   # Test configuration
   sudo nginx -t
   
   # Restart nginx
   sudo systemctl restart nginx
   ```

3. **Port conflicts**
   ```bash
   # Check what's using ports
   sudo lsof -i :5000
   sudo lsof -i :8080
   
   # Kill processes if needed
   sudo kill -9 <PID>
   ```

4. **Permission issues**
   ```bash
   # Fix file permissions
   chmod +x deploy.sh
   sudo chown -R $USER:$USER .
   ```

### Performance Optimization

- **Increase worker processes** in nginx.conf for high load
- **Use Redis** for session storage (included in docker-compose)
- **Add load balancer** with multiple API instances
- **Optimize MediaPipe** model complexity based on requirements

## 📈 Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8080/health

# Nginx health
curl -I http://localhost:8080

# System resources
htop
nvidia-smi  # If using GPU
```

### Logs

```bash
# API logs
tail -f api.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# System logs
journalctl -f
```

## 🌍 Global Access Setup

### Router Configuration

1. **Port Forwarding**: Forward ports 80, 8080, 443 to your server
2. **Dynamic DNS**: Set up DDNS if you have a dynamic IP
3. **Firewall**: Ensure ports are open in your router's firewall

### Domain Setup (Optional)

1. Register a domain name
2. Point it to your public IP
3. Update nginx.conf with your domain name
4. Add SSL certificates for HTTPS

### SSL Certificate (Production)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## 📄 License

This project is open source. See LICENSE file for details. 