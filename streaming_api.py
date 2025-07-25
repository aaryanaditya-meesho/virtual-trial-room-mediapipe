from flask import Flask, Response, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import base64
import numpy as np
import json
import threading
import time
import os
import requests
from shoulder_distance import ShoulderDistanceCalculator
import io
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shoulder_distance_secret_key'

# Enable CORS for all domains with security configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
socketio = SocketIO(app, cors_allowed_origins="*")

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    # CORS headers (additional to Flask-CORS)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Remove server information for security
    response.headers.pop('Server', None)
    
    return response

# Global variables
calculator = ShoulderDistanceCalculator()
current_frame = None
processed_frame = None
frame_lock = threading.Lock()
is_processing = False

class VideoStreamProcessor:
    def __init__(self):
        self.calculator = ShoulderDistanceCalculator()
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()
        
        # Resolution-aware calibration
        self.reference_resolution = (640, 480)  # Standard reference resolution
        self.reference_calibration = 650.0 / 96.0  # 6.77 pixels per cm at reference resolution
        self.current_resolution = None
        self.dynamic_calibration = None
        
        # Display calibration for frontend
        self.display_calibration = None
        self.display_multiplier = 1.0
        
        # Store latest frame for virtual try-on
        self.latest_frame = None
        self.latest_processed_frame = None
        
    def calculate_resolution_multiplier(self, frame_width, frame_height):
        """Calculate resolution multiplier to maintain consistent measurements"""
        ref_width, ref_height = self.reference_resolution
        
        # Calculate scaling factors for both dimensions
        width_scale = frame_width / ref_width
        height_scale = frame_height / ref_height
        
        # Use average of both scales to maintain aspect ratio compensation
        resolution_multiplier = (width_scale + height_scale) / 2
        
        return 1/(1.13)
    
    def set_display_calibration(self, video_width, video_height, display_width, display_height, screen_width, screen_height, device_pixel_ratio):
        """Set display calibration based on frontend dimensions"""
        self.display_calibration = {
            'video_width': video_width,
            'video_height': video_height,
            'display_width': display_width,
            'display_height': display_height,
            'screen_width': screen_width,
            'screen_height': screen_height,
            'device_pixel_ratio': device_pixel_ratio
        }
        
        # Calculate display multiplier (how much bigger/smaller the display is vs video)
        video_scale = (video_width + video_height) / 2
        display_scale = (display_width + display_height) / 2
        self.display_multiplier = display_scale / video_scale if video_scale > 0 else 1.0
        
        print(f"📱 Display Calibration Set:")
        print(f"   Video: {video_width}x{video_height}")
        print(f"   Display: {display_width}x{display_height}")
        print(f"   Screen: {screen_width}x{screen_height}")
        print(f"   Device Pixel Ratio: {device_pixel_ratio}")
        print(f"   Display Multiplier: {self.display_multiplier:.2f}")

    def update_dynamic_calibration(self, frame_width, frame_height):
        """Update calibration based on current frame resolution and display size"""
        current_res = (frame_width, frame_height)
        
        if self.current_resolution != current_res:
            self.current_resolution = current_res
            base_multiplier = self.calculate_resolution_multiplier(frame_width, frame_height)
            
            # Apply display scaling correction
            total_multiplier = base_multiplier * self.display_multiplier
            
            # Always adjust calibration for current resolution and display
            self.dynamic_calibration = self.reference_calibration * total_multiplier
            
            # Force update the calculator's calibration for consistency
            self.calculator.pixels_per_cm = self.dynamic_calibration
            
            print(f"🎯 Resolution: {frame_width}x{frame_height}")
            print(f"📐 Base Multiplier: {base_multiplier:.2f}, Display Multiplier: {self.display_multiplier:.2f}")
            print(f"🔧 Total Multiplier: {total_multiplier:.2f}, Final Calibration: {self.dynamic_calibration:.2f} px/cm")
            print(f"📏 Expected for 96cm: {650 * total_multiplier:.0f}px at current setup")
        
    def process_frame(self, frame):
        """Process a frame and return the processed frame with measurements"""
        try:
            # Store the original clean frame BEFORE any processing for virtual try-on
            self.latest_frame = frame.copy()
            
            # Update calibration based on frame resolution
            frame_height, frame_width = frame.shape[:2]
            self.update_dynamic_calibration(frame_width, frame_height)
            
            # Process the frame using shoulder distance calculator
            processed_frame, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, confidence, scale_info, z_info = self.calculator.process_frame(frame)
            
            # Store the processed frame (with overlays) separately
            self.latest_processed_frame = processed_frame.copy()
            
            # Calculate FPS
            current_time = time.time()
            if current_time - self.last_time > 0:
                self.fps = 1 / (current_time - self.last_time)
            self.last_time = current_time
            self.frame_count += 1
            
            # Add info overlay
            z_display = z_info if self.calculator.show_z_info else None
            self.calculator.add_info_overlay(processed_frame, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, self.fps, confidence, scale_info, z_display)
            
            # Create measurement data with resolution info
            measurements = {
                'shoulder_3d': float(shoulder_3d),
                'shoulder_pixels': float(shoulder_pixels),
                'shoulder_cm': float(shoulder_cm) if shoulder_cm else None,
                'waist_3d': float(waist_3d),
                'waist_pixels': float(waist_pixels),
                'waist_cm': float(waist_cm) if waist_cm else None,
                'confidence': float(confidence),
                'fps': float(self.fps),
                'frame_count': self.frame_count,
                'scale_info': scale_info,
                'z_info': z_info,
                'timestamp': current_time,
                                 'resolution': {
                     'width': frame_width,
                     'height': frame_height,
                     'multiplier': self.calculate_resolution_multiplier(frame_width, frame_height),
                     'display_multiplier': float(self.display_multiplier),
                     'dynamic_calibration': float(self.dynamic_calibration) if self.dynamic_calibration else None,
                     'display_info': self.display_calibration
                 }
            }
            
            return processed_frame, measurements
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, None

# Global video processor
video_processor = VideoStreamProcessor()

@app.route('/')
def index():
    """Serve the main interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shoulder Distance API - Live Stream</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
            .video-container { display: flex; gap: 20px; margin-bottom: 20px; }
            .video-section { flex: 1; }
            video, canvas { width: 100%; max-width: 480px; border: 2px solid #ddd; border-radius: 5px; }
            .controls { margin: 20px 0; }
            button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .measurements { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .measurement-item { margin: 5px 0; padding: 5px; background: white; border-left: 4px solid #007bff; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .status.connected { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .status.disconnected { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .api-info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Shoulder Distance API - Live Stream</h1>
            
            <div class="status" id="status">Disconnected</div>
            
            <div class="video-container">
                <div class="video-section">
                    <h3>📹 Input Stream (Your Camera)</h3>
                    <video id="inputVideo" autoplay muted></video>
                </div>
                <div class="video-section">
                    <h3>🔍 Processed Stream (With Measurements)</h3>
                    <canvas id="outputCanvas"></canvas>
                </div>
            </div>
            
                         <div class="controls">
                 <button id="startBtn" onclick="startStream()">Start Camera</button>
                 <button id="stopBtn" onclick="stopStream()" disabled>Stop Camera</button>
                 <button onclick="toggleCalibration()">Auto Calibrate</button>
                 <button onclick="toggleZInfo()">Toggle Z Info</button>
                 <div style="margin-top: 10px;">
                     <label>Calibration Multiplier: </label>
                     <input type="range" id="multiplierSlider" min="0.1" max="3.0" step="0.1" value="1.0" onchange="updateMultiplier(this.value)">
                     <span id="multiplierValue">1.0x</span>
                                           <button onclick="resetCalibration()">Reset</button>
                  </div>
                  <div style="margin-top: 10px;">
                      <small>💡 Tip: Adjust multiplier if measurements seem too large/small</small>
                  </div>
                  
                  <!-- Virtual Try-On Section -->
                  <div style="margin-top: 20px; padding: 15px; border: 2px dashed #ccc; border-radius: 10px;">
                      <h3>🎭 Virtual Try-On</h3>
                      <input type="file" id="clothingImage" accept="image/*" style="margin: 5px 0;">
                      <button onclick="performTryOn()" id="tryOnBtn">Try On Outfit</button>
                      <div id="tryOnStatus" style="margin-top: 10px; font-size: 14px;"></div>
                  </div>
             </div>
            
            <div class="measurements" id="measurements">
                <h3>📏 Real-time Measurements</h3>
                <div id="measurementData">No measurements yet...</div>
            </div>
            
            <!-- Try-On Result Display -->
            <div id="tryOnResult" style="margin-top: 20px; text-align: center; display: none; padding: 20px; background: rgba(0,0,0,0.1); border-radius: 10px;">
                <h3>🎭 Virtual Try-On Result</h3>
                <img id="resultImage" style="max-width: 100%; max-height: 500px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                <div id="resultInfo" style="margin-top: 10px; font-size: 14px; color: #666;"></div>
            </div>
            
            <div class="api-info">
                <h3>🔧 API Endpoints</h3>
                <p><strong>WebSocket:</strong> Connect to <code>ws://localhost:8000</code> for real-time streaming</p>
                <p><strong>REST API:</strong> POST to <code>/process_image</code> for single image processing</p>
                <p><strong>Health Check:</strong> GET <code>/health</code></p>
                <p><strong>Status:</strong> GET <code>/status</code></p>
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.3.2/socket.io.js"></script>
        <script>
            let socket;
            let inputVideo;
            let outputCanvas;
            let ctx;
            let isStreaming = false;
            let mediaStream;

            function initializeComponents() {
                inputVideo = document.getElementById('inputVideo');
                outputCanvas = document.getElementById('outputCanvas');
                ctx = outputCanvas.getContext('2d');
                
                // Connect to WebSocket
                socket = io();
                
                socket.on('connect', function() {
                    document.getElementById('status').textContent = 'Connected to server';
                    document.getElementById('status').className = 'status connected';
                });
                
                                 socket.on('disconnect', function() {
                     document.getElementById('status').textContent = 'Disconnected from server';
                     document.getElementById('status').className = 'status disconnected';
                 });
                 
                 socket.on('status', function(data) {
                     console.log('Status:', data.message);
                     showStatusMessage(data.message);
                 });
                 
                 socket.on('error', function(data) {
                     console.error('Error:', data.message);
                     showStatusMessage('Error: ' + data.message, 'error');
                 });
                
                socket.on('processed_frame', function(data) {
                    // Display processed frame
                    const img = new Image();
                    img.onload = function() {
                        outputCanvas.width = img.width;
                        outputCanvas.height = img.height;
                        ctx.drawImage(img, 0, 0);
                    };
                    img.src = 'data:image/jpeg;base64,' + data.frame;
                    
                    // Update measurements
                    if (data.measurements) {
                        updateMeasurements(data.measurements);
                    }
                });
            }

                         async function startStream() {
                 try {
                     mediaStream = await navigator.mediaDevices.getUserMedia({ 
                         video: { 
                             width: { ideal: 1280 }, 
                             height: { ideal: 720 },
                             facingMode: 'user'
                         } 
                     });
                     inputVideo.srcObject = mediaStream;
                     
                     // Wait for video to be ready
                     await new Promise(resolve => {
                         inputVideo.onloadedmetadata = resolve;
                     });
                     
                     // Get actual video dimensions
                     const videoWidth = inputVideo.videoWidth;
                     const videoHeight = inputVideo.videoHeight;
                     
                     // Get display dimensions
                     const displayWidth = inputVideo.clientWidth;
                     const displayHeight = inputVideo.clientHeight;
                     
                     console.log(`Video: ${videoWidth}x${videoHeight}, Display: ${displayWidth}x${displayHeight}`);
                     
                     // Send display calibration info to server
                     socket.emit('display_calibration', {
                         video_width: videoWidth,
                         video_height: videoHeight,
                         display_width: displayWidth,
                         display_height: displayHeight,
                         screen_width: window.screen.width,
                         screen_height: window.screen.height,
                         device_pixel_ratio: window.devicePixelRatio
                     });
                     
                     isStreaming = true;
                     document.getElementById('startBtn').disabled = true;
                     document.getElementById('stopBtn').disabled = false;
                     
                     // Start sending frames
                     sendFrames();
                 } catch (err) {
                     alert('Error accessing camera: ' + err.message);
                 }
             }

            function stopStream() {
                if (mediaStream) {
                    mediaStream.getTracks().forEach(track => track.stop());
                }
                isStreaming = false;
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }

            function sendFrames() {
                if (!isStreaming) return;
                
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = inputVideo.videoWidth;
                canvas.height = inputVideo.videoHeight;
                
                ctx.drawImage(inputVideo, 0, 0);
                
                const dataURL = canvas.toDataURL('image/jpeg', 0.8);
                const base64Data = dataURL.split(',')[1];
                
                socket.emit('process_frame', { frame: base64Data });
                
                setTimeout(sendFrames, 100); // Send ~10 FPS
            }

            function updateMeasurements(measurements) {
                let html = '<div class="measurement-item"><strong>👥 Shoulder:</strong> ';
                if (measurements.shoulder_cm) {
                    html += `${measurements.shoulder_cm.toFixed(1)} cm (${measurements.shoulder_pixels.toFixed(0)} px)`;
                } else {
                    html += `${measurements.shoulder_pixels.toFixed(0)} pixels`;
                }
                html += '</div>';
                
                html += '<div class="measurement-item"><strong>⚖️ Waist:</strong> ';
                if (measurements.waist_cm) {
                    html += `${measurements.waist_cm.toFixed(1)} cm (${measurements.waist_pixels.toFixed(0)} px)`;
                } else {
                    html += `${measurements.waist_pixels.toFixed(0)} pixels`;
                }
                html += '</div>';
                
                html += `<div class="measurement-item"><strong>🎯 Confidence:</strong> ${(measurements.confidence * 100).toFixed(1)}%</div>`;
                html += `<div class="measurement-item"><strong>⚡ FPS:</strong> ${measurements.fps.toFixed(1)}</div>`;
                                 html += `<div class="measurement-item"><strong>📐 Scale:</strong> ${measurements.scale_info}</div>`;
                 
                 if (measurements.resolution) {
                     html += `<div class="measurement-item"><strong>📱 Video:</strong> ${measurements.resolution.width}x${measurements.resolution.height}</div>`;
                     html += `<div class="measurement-item"><strong>📺 Display:</strong> ${measurements.resolution.display_multiplier.toFixed(2)}x scale</div>`;
                     if (measurements.resolution.dynamic_calibration) {
                         html += `<div class="measurement-item"><strong>🎯 Calibration:</strong> ${measurements.resolution.dynamic_calibration.toFixed(2)} px/cm</div>`;
                     }
                     // Show display info if available
                     if (measurements.resolution.display_info) {
                         const display = measurements.resolution.display_info;
                         html += `<div class="measurement-item"><strong>🖥️ Screen:</strong> ${display.display_width}x${display.display_height} (${display.device_pixel_ratio}x DPR)</div>`;
                     }
                 }
                 
                 if (measurements.z_info) {
                     html += `<div class="measurement-item"><strong>📊 Depth Info:</strong> Shoulder Z-diff: ${measurements.z_info.shoulder_z_diff.toFixed(4)}, Waist Z-diff: ${measurements.z_info.waist_z_diff.toFixed(4)}</div>`;
                 }
                
                document.getElementById('measurementData').innerHTML = html;
            }

            function toggleCalibration() {
                socket.emit('calibrate', { preset: true });
            }

                         function toggleZInfo() {
                 socket.emit('toggle_z_info');
             }

             function updateMultiplier(value) {
                 document.getElementById('multiplierValue').textContent = value + 'x';
                 socket.emit('calibrate', { multiplier: parseFloat(value) });
             }

                           function resetCalibration() {
                  document.getElementById('multiplierSlider').value = '1.0';
                  document.getElementById('multiplierValue').textContent = '1.0x';
                  socket.emit('calibrate', { preset: true });
              }
              
              // Virtual Try-On Functions
              function performTryOn() {
                  const clothingInput = document.getElementById('clothingImage');
                  const statusDiv = document.getElementById('tryOnStatus');
                  const tryOnBtn = document.getElementById('tryOnBtn');
                  
                  if (!clothingInput.files || clothingInput.files.length === 0) {
                      showTryOnStatus('Please select a clothing image first', 'error');
                      return;
                  }
                  
                  const formData = new FormData();
                  formData.append('clothing_image', clothingInput.files[0]);
                  
                  // Disable button and show loading
                  tryOnBtn.disabled = true;
                  tryOnBtn.textContent = 'Processing...';
                  showTryOnStatus('🎭 Creating virtual try-on... This may take 30-60 seconds', 'info');
                  
                  fetch('/virtual-tryon', {
                      method: 'POST',
                      body: formData
                  })
                  .then(response => response.json())
                  .then(data => {
                      if (data.success) {
                          showTryOnResult(data.result_image, data.result_filename, data.seed);
                          showTryOnStatus('✅ Virtual try-on completed successfully!', 'success');
                      } else {
                          showTryOnStatus('❌ Error: ' + data.error, 'error');
                          if (data.instructions) {
                              showTryOnStatus('💡 ' + data.message + '. Run: ' + data.instructions, 'info');
                          }
                      }
                  })
                  .catch(error => {
                      console.error('Try-on error:', error);
                      showTryOnStatus('❌ Network error: ' + error.message, 'error');
                  })
                  .finally(() => {
                      // Re-enable button
                      tryOnBtn.disabled = false;
                      tryOnBtn.textContent = 'Try On Outfit';
                  });
              }
              
              function showTryOnStatus(message, type = 'info') {
                  const statusDiv = document.getElementById('tryOnStatus');
                  statusDiv.textContent = message;
                  statusDiv.className = type;
                  
                  // Style based on type
                  if (type === 'error') {
                      statusDiv.style.color = '#ff4444';
                  } else if (type === 'success') {
                      statusDiv.style.color = '#44ff44';
                  } else {
                      statusDiv.style.color = '#4444ff';
                  }
              }
              
              function showTryOnResult(imageBase64, filename, seed) {
                  const resultDiv = document.getElementById('tryOnResult');
                  const resultImg = document.getElementById('resultImage');
                  const resultInfo = document.getElementById('resultInfo');
                  
                  resultImg.src = imageBase64;
                  resultInfo.innerHTML = `<strong>Result saved as:</strong> ${filename}<br><strong>Seed:</strong> ${seed}`;
                  resultDiv.style.display = 'block';
                  
                  // Scroll to result
                  resultDiv.scrollIntoView({ behavior: 'smooth' });
              }

             function showStatusMessage(message, type = 'info') {
                 // Create or update status display
                 let statusDiv = document.getElementById('statusMessage');
                 if (!statusDiv) {
                     statusDiv = document.createElement('div');
                     statusDiv.id = 'statusMessage';
                     statusDiv.style.cssText = 'position: fixed; top: 10px; right: 10px; padding: 10px; border-radius: 5px; color: white; z-index: 1000; max-width: 300px;';
                     document.body.appendChild(statusDiv);
                 }
                 
                 statusDiv.textContent = message;
                 statusDiv.style.backgroundColor = type === 'error' ? '#f44336' : '#4CAF50';
                 statusDiv.style.display = 'block';
                 
                 // Auto-hide after 3 seconds
                 setTimeout(() => {
                     statusDiv.style.display = 'none';
                 }, 3000);
             }

             // Initialize when page loads
             document.addEventListener('DOMContentLoaded', initializeComponents);
        </script>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'shoulder-distance-api',
        'timestamp': time.time()
    })

@app.route('/status')
def status():
    """Get current status and configuration"""
    return jsonify({
        'is_processing': is_processing,
        'calibration': {
            'pixels_per_cm': calculator.pixels_per_cm,
            'user_calibration': calculator.user_calibration,
            'has_saved_calibration': calculator.pixels_per_cm is not None
        },
        'show_z_info': calculator.show_z_info,
        'endpoints': {
            'websocket': 'ws://localhost:8000',
            'web_interface': 'http://localhost:8000',
            'process_image': 'http://localhost:8000/process_image',
            'virtual_tryon': 'http://localhost:8000/virtual-tryon',
            'health': 'http://localhost:8000/health'
        },
        'timestamp': time.time()
    })

@app.route('/virtual-tryon', methods=['POST'])
def virtual_tryon():
    """Virtual try-on endpoint requiring both clothing and avatar images"""
    for i in range(10):
        print("virtual try on api called")
    try:
        # Check if clothing image is provided
        if 'clothing_image' not in request.files:
            return jsonify({'error': 'No clothing image provided'}), 400
        
        clothing_file = request.files['clothing_image']
        if clothing_file.filename == '':
            return jsonify({'error': 'No clothing image selected'}), 400
        
        # Check if avatar image is provided (now required)
        if 'avatar_image' not in request.files:
            return jsonify({'error': 'No avatar image provided. Please upload both clothing and avatar images.'}), 400
            
        avatar_file = request.files['avatar_image']
        if avatar_file.filename == '':
            return jsonify({'error': 'No avatar image selected. Please upload both clothing and avatar images.'}), 400
        
        # Get original file extension for clothing image
        original_filename = clothing_file.filename.lower()
        if original_filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            if original_filename.endswith('.png'):
                clothing_ext = '.png'
            elif original_filename.endswith('.webp'):
                clothing_ext = '.webp'
            else:
                clothing_ext = '.jpg'
        else:
            clothing_ext = '.jpg'  # Default to JPG
            
        # Save clothing image temporarily with proper extension
        clothing_filename = f"temp_clothing_{int(time.time())}{clothing_ext}"
        clothing_path = os.path.join(os.getcwd(), clothing_filename)
        clothing_file.save(clothing_path)
        
        # Handle avatar image - use uploaded file
        avatar_filename = f"temp_avatar_{int(time.time())}.jpg"
        avatar_path = os.path.join(os.getcwd(), avatar_filename)
        
        # Use uploaded avatar image
        print(f"📸 Using uploaded avatar image: {avatar_file.filename}")
        avatar_file.save(avatar_path)
        
        # Get RapidAPI key from environment or use placeholder
        rapidapi_key = os.getenv('RAPIDAPI_KEY', '3b32b26a5bmshc04f14a1db17c69p175b48jsnbc94d160d90d')
        
        if rapidapi_key == 'YOUR_RAPIDAPI_KEY_HERE':
            # Cleanup temp files
            try:
                os.remove(clothing_path)
                os.remove(avatar_path)
            except:
                pass
            return jsonify({
                'error': 'RapidAPI key not configured',
                'message': 'Please set the RAPIDAPI_KEY environment variable with your RapidAPI key',
                'instructions': 'export RAPIDAPI_KEY=your_actual_key_here'
            }), 400
        
        # Call RapidAPI Try-On service
        url = "https://try-on-diffusion.p.rapidapi.com/try-on-file"
        
        headers = {
            "x-rapidapi-host": "try-on-diffusion.p.rapidapi.com",
            "x-rapidapi-key": rapidapi_key
        }
        
        # Prepare files with proper MIME types
        with open(clothing_path, 'rb') as clothing_img, open(avatar_path, 'rb') as avatar_img:
            # Determine MIME types based on file extensions
            clothing_mime = 'image/png' if clothing_ext == '.png' else 'image/webp' if clothing_ext == '.webp' else 'image/jpeg'
            avatar_mime = 'image/jpeg'
            
            files = {
                'clothing_image': (clothing_filename, clothing_img, clothing_mime),
                'avatar_image': (avatar_filename, avatar_img, avatar_mime)
            }
            
            print(f"🎭 Calling virtual try-on API...")
            print(f"   Clothing: {clothing_filename} ({clothing_mime})")
            print(f"   Avatar: {avatar_filename} ({avatar_mime}) - Uploaded")
            response = requests.post(url, headers=headers, files=files, timeout=30)
        
        # Cleanup temp files
        try:
            os.remove(clothing_path)
            os.remove(avatar_path)
        except:
            pass
        
        if response.status_code == 200:
            # Save the result image
            result_filename = f"tryon_result_{int(time.time())}.jpg"
            result_path = os.path.join(os.getcwd(), result_filename)
            
            with open(result_path, 'wb') as f:
                f.write(response.content)
            
            # Convert result to base64 for frontend display
            result_base64 = base64.b64encode(response.content).decode('utf-8')
            
            print(f"✅ Virtual try-on successful! Result saved as {result_filename}")
            
            return jsonify({
                'success': True,
                'message': 'Virtual try-on completed successfully',
                'result_image_base64': result_base64,
                'result_image': f'data:image/jpeg;base64,{result_base64}',
                'result_filename': result_filename,
                'seed': response.headers.get('X-Seed', 'unknown')
            })
        else:
            error_msg = f"RapidAPI error: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            
            print(f"❌ Virtual try-on failed: {error_msg}")
            return jsonify({'error': error_msg}), response.status_code
            
    except Exception as e:
        print(f"❌ Virtual try-on error: {str(e)}")
        return jsonify({'error': f'Virtual try-on failed: {str(e)}'}), 500

@app.route('/test-upload', methods=['POST'])
def test_upload():
    """Test endpoint to verify file upload functionality"""
    try:
        if 'clothing_image' not in request.files:
            return jsonify({'error': 'No clothing image provided'}), 400
        
        clothing_file = request.files['clothing_image']
        if clothing_file.filename == '':
            return jsonify({'error': 'No clothing image selected'}), 400
        
        if 'avatar_image' not in request.files:
            return jsonify({'error': 'No avatar image provided'}), 400
            
        avatar_file = request.files['avatar_image']
        if avatar_file.filename == '':
            return jsonify({'error': 'No avatar image selected'}), 400
        
        # Test the same file processing logic
        original_filename = clothing_file.filename.lower()
        if original_filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            if original_filename.endswith('.png'):
                clothing_ext = '.png'
            elif original_filename.endswith('.webp'):
                clothing_ext = '.webp'
            else:
                clothing_ext = '.jpg'
        else:
            clothing_ext = '.jpg'
            
        clothing_filename = f"test_clothing_{int(time.time())}{clothing_ext}"
        avatar_filename = f"test_avatar_{int(time.time())}.jpg"
        
        # Test avatar image save
        avatar_path = os.path.join(os.getcwd(), avatar_filename)
        avatar_file.save(avatar_path)
        
        # Get file sizes
        clothing_size = len(clothing_file.read())
        clothing_file.seek(0)  # Reset file pointer
        
        avatar_size = os.path.getsize(avatar_path)
        
        # Cleanup
        try:
            os.remove(avatar_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'clothing_file': {
                'filename': clothing_file.filename,
                'processed_filename': clothing_filename,
                'extension': clothing_ext,
                'size': clothing_size
            },
            'avatar_file': {
                'filename': avatar_file.filename,
                'processed_filename': avatar_filename,
                'size': avatar_size
            },
            'message': 'Both images processed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Test failed: {str(e)}'}), 500

@app.route('/process_image', methods=['POST'])
def process_image():
    """Process a single image via REST API"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read image
        image_data = file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Process frame
        processed_frame, measurements = video_processor.process_frame(frame)
        
        # Encode processed frame
        _, buffer = cv2.imencode('.jpg', processed_frame)
        encoded_frame = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'processed_image': encoded_frame,
            'measurements': measurements,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print('Client connected')
    emit('status', {'message': 'Connected to Shoulder Distance API'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print('Client disconnected')

@socketio.on('process_frame')
def handle_process_frame(data):
    """Process incoming frame from WebSocket"""
    global is_processing
    
    try:
        is_processing = True
        
        # Decode base64 image
        image_data = base64.b64decode(data['frame'])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is not None:
            # Process frame
            processed_frame, measurements = video_processor.process_frame(frame)
            
            # Encode processed frame
            _, buffer = cv2.imencode('.jpg', processed_frame)
            encoded_frame = base64.b64encode(buffer).decode('utf-8')
            
            # Send back processed frame and measurements
            emit('processed_frame', {
                'frame': encoded_frame,
                'measurements': measurements
            })
        
        is_processing = False
        
    except Exception as e:
        print(f"Error processing frame: {e}")
        is_processing = False
        emit('error', {'message': str(e)})

@socketio.on('calibrate')
def handle_calibrate(data):
    """Handle calibration request"""
    try:
        if data.get('preset', False):
            # Reset to automatic resolution-aware calibration
            if video_processor.current_resolution:
                video_processor.calculator.pixels_per_cm = video_processor.dynamic_calibration
                emit('status', {'message': f'Reset to auto calibration: {video_processor.dynamic_calibration:.2f} px/cm for {video_processor.current_resolution[0]}x{video_processor.current_resolution[1]}'})
            else:
                video_processor.calculator.pixels_per_cm = video_processor.reference_calibration
                emit('status', {'message': f'Reset to base calibration: {video_processor.reference_calibration:.2f} px/cm'})
        elif 'pixels_per_cm' in data:
            # Manual calibration override
            new_calibration = float(data['pixels_per_cm'])
            calculator.pixels_per_cm = new_calibration
            emit('status', {'message': f'Applied manual calibration: {new_calibration:.2f} px/cm'})
        elif 'multiplier' in data:
            # Apply custom multiplier to current dynamic calibration
            multiplier = float(data['multiplier'])
            if video_processor.dynamic_calibration:
                new_calibration = video_processor.dynamic_calibration * multiplier
                calculator.pixels_per_cm = new_calibration
                resolution_text = f"{video_processor.current_resolution[0]}x{video_processor.current_resolution[1]}" if video_processor.current_resolution else "unknown"
                emit('status', {'message': f'Applied {multiplier:.1f}x multiplier: {new_calibration:.2f} px/cm ({resolution_text})'})
            else:
                # Fallback to base calibration
                new_calibration = video_processor.reference_calibration * multiplier
                calculator.pixels_per_cm = new_calibration
                emit('status', {'message': f'Applied {multiplier:.1f}x to base: {new_calibration:.2f} px/cm'})
        else:
            emit('error', {'message': 'Invalid calibration data'})
    except Exception as e:
        emit('error', {'message': f'Calibration error: {str(e)}'})

@socketio.on('toggle_z_info')
def handle_toggle_z_info():
    """Toggle Z coordinate information display"""
    calculator.show_z_info = not calculator.show_z_info
    status = "ON" if calculator.show_z_info else "OFF"
    emit('status', {'message': f'Z coordinate display: {status}'})

@socketio.on('display_calibration')
def handle_display_calibration(data):
    """Handle display calibration from frontend"""
    try:
        video_processor.set_display_calibration(
            data['video_width'],
            data['video_height'], 
            data['display_width'],
            data['display_height'],
            data['screen_width'],
            data['screen_height'],
            data['device_pixel_ratio']
        )
        emit('status', {'message': f'Display calibration updated: {data["video_width"]}x{data["video_height"]} → {data["display_width"]}x{data["display_height"]}'})
    except Exception as e:
        emit('error', {'message': f'Display calibration error: {str(e)}'})

@socketio.on('reset_calibration')
def handle_reset_calibration():
    """Reset calibration to default"""
    calculator.pixels_per_cm = None
    import os
    if os.path.exists(calculator.calibration_file):
        os.remove(calculator.calibration_file)
    emit('status', {'message': 'Calibration reset to default'})

if __name__ == '__main__':
    print("🚀 Starting Shoulder Distance Streaming API...")
    print("📡 WebSocket endpoint: ws://localhost:8000")
    print("🌐 Web interface: http://localhost:8000")
    print("🔧 REST API: http://localhost:8000/process_image")
    print("❤️ Health check: http://localhost:8000/health")
    
    socketio.run(app, 
                host='0.0.0.0', 
                port=8000, 
                debug=True,
                allow_unsafe_werkzeug=True) 