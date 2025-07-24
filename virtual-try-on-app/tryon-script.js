// Global variables
let userImage = null;
let clothingImage = null;
let resultCanvas = null;
let resultContext = null;
let currentAdjustments = {
    size: 100,
    positionX: 0,
    positionY: 0
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupImageUploads();
    setupCanvas();
    setupDragAndDrop();
    
    // Check for pre-selected fabric from catalog
    checkForPreSelectedFabric();
    
    console.log('✂️ Virtual Try-On Studio initialized');
}

// Check for pre-selected fabric from catalog
function checkForPreSelectedFabric() {
    const selectedFabric = localStorage.getItem('selectedFabric');
    const selectedFabricName = localStorage.getItem('selectedFabricName');
    const tryOnMode = localStorage.getItem('tryOnMode');
    
    if (selectedFabric && selectedFabricName) {
        console.log(`🎨 Pre-selected fabric detected: ${selectedFabricName}`);
        
        // Load the pre-selected fabric as clothing image
        const img = new Image();
        img.onload = () => {
            clothingImage = img;
            displayImagePreview(img, 'clothingImagePreview', 'clothingUploadArea');
            
            // Update UI to show fabric is from catalog
            const clothingArea = document.getElementById('clothingUploadArea');
            const existingBadge = clothingArea.querySelector('.catalog-badge');
            if (!existingBadge) {
                const catalogBadge = document.createElement('div');
                catalogBadge.className = 'catalog-badge';
                catalogBadge.innerHTML = '🏷️ From Catalog';
                clothingArea.appendChild(catalogBadge);
            }
            
            showNotification(`✨ ${selectedFabricName} loaded from catalog!`, 'success');
            checkReadyState();
            
            // If camera mode was selected, open webcam
            if (tryOnMode === 'camera') {
                setTimeout(() => {
                    showNotification('📸 Camera mode selected - click "Use Webcam" to start', 'info');
                }, 1500);
            }
        };
        
        img.onerror = () => {
            console.error('Failed to load pre-selected fabric:', selectedFabric);
            showNotification('❌ Failed to load selected fabric', 'error');
        };
        
        img.src = selectedFabric;
        
        // Clear the stored values after loading
        localStorage.removeItem('selectedFabric');
        localStorage.removeItem('selectedFabricName');
        localStorage.removeItem('tryOnMode');
    }
}

// Image Upload Handling
function setupImageUploads() {
    const userImageInput = document.getElementById('userImageInput');
    const clothingImageInput = document.getElementById('clothingImageInput');
    
    userImageInput.addEventListener('change', (e) => handleImageUpload(e, 'user'));
    clothingImageInput.addEventListener('change', (e) => handleImageUpload(e, 'clothing'));
}

function handleImageUpload(event, type) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            if (type === 'user') {
                userImage = img;
                displayImagePreview(img, 'userImagePreview', 'userUploadArea');
                showNotification('👤 User photo uploaded successfully!', 'success');
            } else {
                clothingImage = img;
                displayImagePreview(img, 'clothingImagePreview', 'clothingUploadArea');
                showNotification('👕 Clothing image uploaded successfully!', 'success');
            }
            checkReadyState();
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function displayImagePreview(img, previewId, uploadAreaId) {
    const preview = document.getElementById(previewId);
    const uploadArea = document.getElementById(uploadAreaId);
    
    preview.src = img.src;
    preview.style.display = 'block';
    uploadArea.classList.add('has-image');
    
    // Hide placeholder
    const placeholder = uploadArea.querySelector('.upload-placeholder');
    if (placeholder) {
        placeholder.style.display = 'none';
    }
}

// Preset Clothing Loading
function loadPresetClothing(src) {
    // Remove selection from other presets
    document.querySelectorAll('.preset-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // Add selection to clicked preset
    event.target.classList.add('selected');
    
    const img = new Image();
    img.onload = () => {
        clothingImage = img;
        displayImagePreview(img, 'clothingImagePreview', 'clothingUploadArea');
        showNotification('👕 Preset clothing selected!', 'success');
        checkReadyState();
    };
    img.src = src;
}

// Canvas Setup
function setupCanvas() {
    resultCanvas = document.getElementById('resultCanvas');
    resultContext = resultCanvas.getContext('2d');
    
    // Set canvas size
    resultCanvas.width = 400;
    resultCanvas.height = 500;
}

// Check if ready for virtual try-on
function checkReadyState() {
    const tryOnBtn = document.getElementById('tryOnBtn');
    
    if (userImage && clothingImage) {
        tryOnBtn.disabled = false;
        tryOnBtn.innerHTML = '<i class="fas fa-magic"></i> Try It On!';
        showNotification('🎉 Ready for virtual try-on!', 'info');
    } else {
        tryOnBtn.disabled = true;
        const missing = [];
        if (!userImage) missing.push('user photo');
        if (!clothingImage) missing.push('clothing item');
        tryOnBtn.innerHTML = `<i class="fas fa-upload"></i> Upload ${missing.join(' & ')}`;
    }
}

// Virtual Try-On Processing
function performVirtualTryOn() {
    if (!userImage || !clothingImage) {
        showNotification('❌ Please upload both images first', 'error');
        return;
    }
    
    showLoadingOverlay();
    
    // Simulate processing time
    setTimeout(() => {
        processVirtualTryOn();
        hideLoadingOverlay();
        showResultActions();
        showNotification('✨ Virtual try-on complete!', 'success');
    }, 3000);
}

function processVirtualTryOn() {
    const canvas = resultCanvas;
    const ctx = resultContext;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate dimensions
    const userAspect = userImage.width / userImage.height;
    const canvasAspect = canvas.width / canvas.height;
    
    let userWidth, userHeight, userX, userY;
    
    if (userAspect > canvasAspect) {
        userHeight = canvas.height;
        userWidth = userHeight * userAspect;
        userX = (canvas.width - userWidth) / 2;
        userY = 0;
    } else {
        userWidth = canvas.width;
        userHeight = userWidth / userAspect;
        userX = 0;
        userY = (canvas.height - userHeight) / 2;
    }
    
    // Draw user image
    ctx.drawImage(userImage, userX, userY, userWidth, userHeight);
    
    // Apply clothing overlay
    applyClothingOverlay(ctx, canvas);
    
    // Show result
    showResult();
}

function applyClothingOverlay(ctx, canvas) {
    const { size, positionX, positionY } = currentAdjustments;
    
    // Calculate clothing dimensions and position
    const clothingScale = size / 100;
    const clothingWidth = canvas.width * 0.6 * clothingScale;
    const clothingHeight = (clothingWidth / clothingImage.width) * clothingImage.height;
    
    const clothingX = (canvas.width - clothingWidth) / 2 + positionX;
    const clothingY = canvas.height * 0.3 + positionY;
    
    // Set blend mode for realistic overlay
    ctx.globalCompositeOperation = 'multiply';
    ctx.globalAlpha = 0.8;
    
    // Draw clothing
    ctx.drawImage(clothingImage, clothingX, clothingY, clothingWidth, clothingHeight);
    
    // Reset blend mode
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1.0;
}

function showResult() {
    const resultContainer = document.getElementById('resultContainer');
    const placeholder = resultContainer.querySelector('.result-placeholder');
    
    placeholder.style.display = 'none';
    resultCanvas.style.display = 'block';
    resultContainer.classList.add('has-result');
    
    // Add success animation
    resultCanvas.classList.add('success-animation');
}

function showResultActions() {
    const resultActions = document.getElementById('resultActions');
    const adjustmentControls = document.getElementById('adjustmentControls');
    
    resultActions.style.display = 'grid';
    adjustmentControls.style.display = 'block';
}

// Adjustment Controls
function adjustClothing() {
    const sizeSlider = document.getElementById('sizeSlider');
    const positionXSlider = document.getElementById('positionXSlider');
    const positionYSlider = document.getElementById('positionYSlider');
    
    const sizeValue = document.getElementById('sizeValue');
    const positionXValue = document.getElementById('positionXValue');
    const positionYValue = document.getElementById('positionYValue');
    
    // Update values
    currentAdjustments.size = parseInt(sizeSlider.value);
    currentAdjustments.positionX = parseInt(positionXSlider.value);
    currentAdjustments.positionY = parseInt(positionYSlider.value);
    
    // Update display
    sizeValue.textContent = currentAdjustments.size + '%';
    positionXValue.textContent = currentAdjustments.positionX + 'px';
    positionYValue.textContent = currentAdjustments.positionY + 'px';
    
    // Re-process if result exists
    if (resultCanvas.style.display !== 'none') {
        processVirtualTryOn();
    }
}

// Webcam Capture
function captureFromWebcam(type) {
    console.log('🎥 Starting webcam capture for:', type);
    showNotification('📷 Requesting camera access...', 'info');
    
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('❌ MediaDevices not supported');
        showNotification('❌ Webcam not supported in this browser', 'error');
        alert('Webcam access is not supported in your browser. Please try Chrome or Safari.');
        return;
    }
    
    console.log('🔍 Checking for available video devices...');
    
    // Enhanced camera request with better constraints
    const constraints = {
        video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user' // Front camera preferred
        }
    };
    
    navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            console.log('✅ Camera access granted!', stream);
            showNotification('✅ Camera access granted!', 'success');
            showWebcamModal(stream, type);
        })
        .catch(err => {
            console.error('❌ Webcam access error:', err);
            let errorMessage = 'Camera access failed. ';
            
            switch(err.name) {
                case 'NotAllowedError':
                    errorMessage += 'Permission denied. Please allow camera access and try again.';
                    break;
                case 'NotFoundError':
                    errorMessage += 'No camera found. Please connect a camera and try again.';
                    break;
                case 'NotReadableError':
                    errorMessage += 'Camera is being used by another application. Please close other camera apps.';
                    break;
                case 'OverconstrainedError':
                    errorMessage += 'Camera constraints not supported. Trying basic settings...';
                    // Retry with basic constraints
                    setTimeout(() => retryWithBasicConstraints(type), 1000);
                    return;
                default:
                    errorMessage += `Error: ${err.message}`;
            }
            
            showNotification(errorMessage, 'error');
            alert(errorMessage);
        });
}

function retryWithBasicConstraints(type) {
    console.log('🔄 Retrying with basic camera constraints...');
    showNotification('🔄 Retrying with basic camera settings...', 'info');
    
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            console.log('✅ Camera working with basic constraints!');
            showNotification('✅ Camera connected!', 'success');
            showWebcamModal(stream, type);
        })
        .catch(err => {
            console.error('❌ Basic constraints also failed:', err);
            showNotification('❌ Camera access completely failed', 'error');
            alert('Camera access failed even with basic settings. Please check your camera permissions in browser settings.');
        });
}

function showWebcamModal(stream, type) {
    console.log('🎬 Creating webcam modal for:', type);
    console.log('📹 Stream details:', stream);
    
    // Create webcam modal
    const modal = document.createElement('div');
    modal.className = 'webcam-modal';
    modal.innerHTML = `
        <div class="webcam-content">
            <div class="webcam-header">
                <h3>📸 Capture ${type === 'user' ? 'Your Photo' : 'Clothing Image'}</h3>
                <button class="close-webcam" onclick="closeWebcam()">×</button>
            </div>
            <div class="webcam-body">
                <div class="video-container">
                    <video id="webcamVideo" autoplay playsinline></video>
                    <div class="camera-overlay">
                        <div class="camera-frame"></div>
                        <div class="camera-instructions">
                            <p>${type === 'user' ? '👤 Position yourself in the frame' : '👕 Show the clothing item clearly'}</p>
                        </div>
                    </div>
                </div>
                <canvas id="captureCanvas" style="display:none;"></canvas>
                <div class="captured-preview" id="capturedPreview" style="display:none;">
                    <h4>📷 Captured Photo:</h4>
                    <img id="previewImage" alt="Captured photo">
                    <div class="preview-actions">
                        <button class="retake-btn" onclick="retakePhoto()">
                            <i class="fas fa-redo"></i> Retake
                        </button>
                        <button class="use-photo-btn" onclick="usePhoto('${type}')">
                            <i class="fas fa-check"></i> Use This Photo
                        </button>
                    </div>
                </div>
            </div>
            <div class="webcam-actions">
                <button class="capture-photo-btn" id="captureBtn" onclick="capturePhoto('${type}')">
                    <i class="fas fa-camera"></i> Take Photo
                </button>
                <div class="webcam-tips">
                    <small>💡 Tips: Ensure good lighting and ${type === 'user' ? 'face the camera directly' : 'show the item clearly'}</small>
                    <small>⌨️ Press SPACEBAR to take photo • ESC to close</small>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Setup video stream
    const video = document.getElementById('webcamVideo');
    video.srcObject = stream;
    
    // Wait for video to load and set proper dimensions
    video.addEventListener('loadedmetadata', () => {
        // Adjust video dimensions for better display
        const aspectRatio = video.videoWidth / video.videoHeight;
        if (aspectRatio > 1) {
            video.style.width = '100%';
            video.style.height = 'auto';
        } else {
            video.style.height = '400px';
            video.style.width = 'auto';
        }
        
        showNotification('📷 Webcam ready! Click "Take Photo" when ready', 'info');
    });
    
    // Store stream reference
    window.currentStream = stream;
    window.currentCaptureType = type;
    
    // Add keyboard listener for spacebar to take photo
    const keyboardHandler = (e) => {
        if (e.code === 'Space' && document.querySelector('.webcam-modal')) {
            e.preventDefault();
            capturePhoto(type);
        } else if (e.code === 'Escape' && document.querySelector('.webcam-modal')) {
            e.preventDefault();
            closeWebcam();
        }
    };
    
    document.addEventListener('keydown', keyboardHandler);
    
    // Store handler for cleanup
    window.webcamKeyboardHandler = keyboardHandler;
}

function capturePhoto(type) {
    const video = document.getElementById('webcamVideo');
    const canvas = document.getElementById('captureCanvas');
    const ctx = canvas.getContext('2d');
    const captureBtn = document.getElementById('captureBtn');
    
    // Disable capture button temporarily
    captureBtn.disabled = true;
    captureBtn.innerHTML = '<i class="fas fa-camera"></i> Capturing...';
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw the current frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Show camera flash effect
    showCameraFlash();
    
    // Convert to data URL for preview
    const dataURL = canvas.toDataURL('image/png');
    
    // Show preview
    showCapturedPreview(dataURL);
    
    // Store the captured image data
    window.capturedImageData = dataURL;
    
    // Re-enable capture button
    setTimeout(() => {
        captureBtn.disabled = false;
        captureBtn.innerHTML = '<i class="fas fa-camera"></i> Take Another';
    }, 500);
    
    showNotification('📸 Photo captured! Review and use or retake', 'success');
}

function showCameraFlash() {
    // Create flash effect
    const flash = document.createElement('div');
    flash.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: white;
        z-index: 9999;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.1s;
    `;
    
    document.body.appendChild(flash);
    
    // Animate flash
    setTimeout(() => flash.style.opacity = '0.8', 10);
    setTimeout(() => flash.style.opacity = '0', 150);
    setTimeout(() => flash.remove(), 300);
}

function showCapturedPreview(dataURL) {
    const preview = document.getElementById('capturedPreview');
    const previewImage = document.getElementById('previewImage');
    const videoContainer = document.querySelector('.video-container');
    
    previewImage.src = dataURL;
    preview.style.display = 'block';
    videoContainer.style.opacity = '0.3';
}

function retakePhoto() {
    const preview = document.getElementById('capturedPreview');
    const videoContainer = document.querySelector('.video-container');
    const captureBtn = document.getElementById('captureBtn');
    
    preview.style.display = 'none';
    videoContainer.style.opacity = '1';
    captureBtn.innerHTML = '<i class="fas fa-camera"></i> Take Photo';
    
    window.capturedImageData = null;
    showNotification('📷 Ready to take another photo', 'info');
}

function usePhoto(type) {
    if (!window.capturedImageData) {
        showNotification('❌ No photo captured yet', 'error');
        return;
    }
    
    // Create image object from captured data
    const img = new Image();
    img.onload = () => {
        if (type === 'user') {
            userImage = img;
            displayImagePreview(img, 'userImagePreview', 'userUploadArea');
            showNotification('👤 User photo set successfully!', 'success');
        } else {
            clothingImage = img;
            displayImagePreview(img, 'clothingImagePreview', 'clothingUploadArea');
            showNotification('👕 Clothing photo set successfully!', 'success');
        }
        checkReadyState();
        closeWebcam();
    };
    img.src = window.capturedImageData;
}

function closeWebcam() {
    // Stop stream
    if (window.currentStream) {
        window.currentStream.getTracks().forEach(track => track.stop());
        window.currentStream = null;
    }
    
    // Remove keyboard listener
    if (window.webcamKeyboardHandler) {
        document.removeEventListener('keydown', window.webcamKeyboardHandler);
        window.webcamKeyboardHandler = null;
    }
    
    // Clear captured data
    window.capturedImageData = null;
    window.currentCaptureType = null;
    
    // Remove modal
    const modal = document.querySelector('.webcam-modal');
    if (modal) {
        modal.remove();
    }
    
    showNotification('📷 Webcam closed', 'info');
}

// Result Actions
function downloadResult() {
    if (!resultCanvas) return;
    
    const link = document.createElement('a');
    link.download = `virtual-tryon-${Date.now()}.png`;
    link.href = resultCanvas.toDataURL();
    link.click();
    
    showNotification('💾 Image downloaded successfully!', 'success');
}

function shareResult() {
    if (!resultCanvas) return;
    
    resultCanvas.toBlob(blob => {
        if (navigator.share) {
            navigator.share({
                title: 'My Virtual Try-On Result',
                text: 'Check out my virtual try-on!',
                files: [new File([blob], 'virtual-tryon.png', { type: 'image/png' })]
            });
        } else {
            // Fallback: copy to clipboard or show share options
            copyImageToClipboard(blob);
        }
    });
}

function copyImageToClipboard(blob) {
    if (navigator.clipboard && navigator.clipboard.write) {
        navigator.clipboard.write([
            new ClipboardItem({ 'image/png': blob })
        ]).then(() => {
            showNotification('📋 Image copied to clipboard!', 'success');
        }).catch(() => {
            showNotification('❌ Could not copy to clipboard', 'error');
        });
    } else {
        showNotification('📱 Share feature not available. Image has been downloaded.', 'info');
        downloadResult();
    }
}

function saveToGallery() {
    // Simulate saving to gallery
    showNotification('💾 Saving to gallery...', 'info');
    
    setTimeout(() => {
        downloadResult();
        showNotification('✅ Saved to gallery!', 'success');
    }, 1000);
}

function resetTryOn() {
    // Reset everything
    userImage = null;
    clothingImage = null;
    currentAdjustments = { size: 100, positionX: 0, positionY: 0 };
    
    // Reset UI
    resetImagePreviews();
    hideResult();
    resetSliders();
    checkReadyState();
    
    showNotification('🔄 Virtual try-on reset!', 'info');
}

function resetImagePreviews() {
    const userPreview = document.getElementById('userImagePreview');
    const clothingPreview = document.getElementById('clothingImagePreview');
    const userUploadArea = document.getElementById('userUploadArea');
    const clothingUploadArea = document.getElementById('clothingUploadArea');
    
    userPreview.style.display = 'none';
    clothingPreview.style.display = 'none';
    userUploadArea.classList.remove('has-image');
    clothingUploadArea.classList.remove('has-image');
    
    // Show placeholders
    userUploadArea.querySelector('.upload-placeholder').style.display = 'block';
    clothingUploadArea.querySelector('.upload-placeholder').style.display = 'block';
    
    // Clear preset selection
    document.querySelectorAll('.preset-item').forEach(item => {
        item.classList.remove('selected');
    });
}

function hideResult() {
    const resultContainer = document.getElementById('resultContainer');
    const placeholder = resultContainer.querySelector('.result-placeholder');
    const resultActions = document.getElementById('resultActions');
    const adjustmentControls = document.getElementById('adjustmentControls');
    
    placeholder.style.display = 'block';
    resultCanvas.style.display = 'none';
    resultContainer.classList.remove('has-result');
    resultActions.style.display = 'none';
    adjustmentControls.style.display = 'none';
}

function resetSliders() {
    document.getElementById('sizeSlider').value = 100;
    document.getElementById('positionXSlider').value = 0;
    document.getElementById('positionYSlider').value = 0;
    
    document.getElementById('sizeValue').textContent = '100%';
    document.getElementById('positionXValue').textContent = '0px';
    document.getElementById('positionYValue').textContent = '0px';
}

// Drag and Drop Setup
function setupDragAndDrop() {
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        area.addEventListener('dragover', handleDragOver);
        area.addEventListener('dragleave', handleDragLeave);
        area.addEventListener('drop', handleDrop);
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type.startsWith('image/')) {
            const type = e.currentTarget.id.includes('user') ? 'user' : 'clothing';
            const event = { target: { files: [file] } };
            handleImageUpload(event, type);
        }
    }
}

// Loading Overlay
function showLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'flex';
    
    // Simulate progress
    animateProgress();
    
    // Update loading text
    const loadingTexts = [
        'Analyzing your photo...',
        'Processing clothing item...',
        'Applying AI fitting algorithms...',
        'Adjusting for perfect fit...',
        'Finalizing your virtual try-on...'
    ];
    
    let textIndex = 0;
    const loadingText = document.getElementById('loadingText');
    
    const textInterval = setInterval(() => {
        if (textIndex < loadingTexts.length) {
            loadingText.textContent = loadingTexts[textIndex];
            textIndex++;
        } else {
            clearInterval(textInterval);
        }
    }, 600);
    
    // Store interval for cleanup
    window.loadingTextInterval = textInterval;
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'none';
    
    // Clear intervals
    if (window.loadingTextInterval) {
        clearInterval(window.loadingTextInterval);
    }
    if (window.progressInterval) {
        clearInterval(window.progressInterval);
    }
}

function animateProgress() {
    const progressFill = document.getElementById('progressFill');
    let progress = 0;
    
    const progressInterval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress > 100) progress = 100;
        
        progressFill.style.width = progress + '%';
        
        if (progress >= 100) {
            clearInterval(progressInterval);
        }
    }, 200);
    
    // Store interval for cleanup
    window.progressInterval = progressInterval;
}

// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#F44336' : type === 'warning' ? '#FF9800' : '#2196F3'};
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
        max-width: 350px;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 4000);
}

// Add notification CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .notification-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 15px;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        opacity: 0.8;
        transition: opacity 0.2s;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
    
    .webcam-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        z-index: 2000;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(5px);
    }
    
    .webcam-content {
        background: white;
        border-radius: 15px;
        padding: 20px;
        max-width: 500px;
        width: 90%;
    }
    
    .webcam-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .webcam-header h3 {
        color: #8B2686;
        margin: 0;
    }
    
    .close-webcam {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
    }
    
         .webcam-body {
         text-align: center;
         margin-bottom: 20px;
     }
     
     .video-container {
         position: relative;
         display: inline-block;
         border-radius: 15px;
         overflow: hidden;
         background: #000;
         margin-bottom: 15px;
         transition: opacity 0.3s;
     }
     
     #webcamVideo {
         display: block;
         max-width: 100%;
         max-height: 400px;
         border-radius: 15px;
     }
     
     .camera-overlay {
         position: absolute;
         top: 0;
         left: 0;
         right: 0;
         bottom: 0;
         pointer-events: none;
     }
     
     .camera-frame {
         position: absolute;
         top: 50%;
         left: 50%;
         transform: translate(-50%, -50%);
         width: 80%;
         height: 80%;
         border: 3px solid rgba(255, 255, 255, 0.8);
         border-radius: 15px;
         box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.3);
     }
     
     .camera-instructions {
         position: absolute;
         bottom: 20px;
         left: 50%;
         transform: translateX(-50%);
         background: rgba(0, 0, 0, 0.7);
         color: white;
         padding: 8px 15px;
         border-radius: 20px;
         font-size: 14px;
         white-space: nowrap;
     }
     
     .captured-preview {
         background: #f8f9fa;
         border-radius: 15px;
         padding: 20px;
         margin: 15px 0;
         text-align: center;
     }
     
     .captured-preview h4 {
         color: #8B2686;
         margin-bottom: 15px;
         font-size: 16px;
     }
     
     .captured-preview img {
         max-width: 100%;
         max-height: 200px;
         border-radius: 10px;
         box-shadow: 0 4px 15px rgba(0,0,0,0.1);
         margin-bottom: 15px;
     }
     
     .preview-actions {
         display: flex;
         gap: 10px;
         justify-content: center;
     }
     
     .retake-btn, .use-photo-btn {
         padding: 10px 20px;
         border: none;
         border-radius: 8px;
         font-size: 14px;
         font-weight: 600;
         cursor: pointer;
         transition: all 0.2s;
         display: flex;
         align-items: center;
         gap: 5px;
     }
     
     .retake-btn {
         background: #f44336;
         color: white;
     }
     
     .retake-btn:hover {
         background: #d32f2f;
         transform: translateY(-2px);
     }
     
     .use-photo-btn {
         background: #4CAF50;
         color: white;
     }
     
     .use-photo-btn:hover {
         background: #388E3C;
         transform: translateY(-2px);
     }
     
     .capture-photo-btn {
         width: 100%;
         padding: 15px;
         background: linear-gradient(135deg, #8B2686 0%, #5B1B6E 100%);
         color: white;
         border: none;
         border-radius: 10px;
         font-size: 16px;
         font-weight: 600;
         cursor: pointer;
         transition: all 0.2s;
         margin-bottom: 10px;
     }
     
     .capture-photo-btn:hover {
         transform: translateY(-2px);
         box-shadow: 0 5px 15px rgba(139, 38, 134, 0.3);
     }
     
     .capture-photo-btn:disabled {
         opacity: 0.6;
         cursor: not-allowed;
         transform: none;
     }
     
     .webcam-tips {
         text-align: center;
         color: #666;
         font-style: italic;
     }
     
     .webcam-tips small {
         display: block;
         margin: 2px 0;
         font-size: 12px;
     }
`;
document.head.appendChild(style); 