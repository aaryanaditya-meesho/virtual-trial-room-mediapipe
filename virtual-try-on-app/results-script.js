// Global variables
let currentResultIndex = 1;
let totalResults = 3;
let availableResults = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeResultsViewer();
});

function initializeResultsViewer() {
    console.log('🖼️ Initializing Results Viewer...');
    
    // Load available results
    loadResults();
    
    // Setup navigation
    updateNavigation();
    
    // Update display
    updateResultDisplay();
    
    console.log('✅ Results Viewer initialized');
}

function loadResults() {
    console.log('📁 Loading available results...');
    
    // Define available result sets (you can modify this based on actual files)
    availableResults = [
        {
            id: 1,
            userImage: 'results/user_1.jpg',
            clothImage: 'results/cloth_1.jpg',
            resultImage: 'results/combined_1.jpg',
            confidence: 95,
            processingTime: '2.3 seconds',
            resolution: '640x480',
            timestamp: new Date().toLocaleString()
        },
        {
            id: 2,
            userImage: 'results/user_2.jpg',
            clothImage: 'results/cloth_2.jpg',
            resultImage: 'results/combined_2.jpg',
            confidence: 89,
            processingTime: '1.8 seconds',
            resolution: '640x480',
            timestamp: new Date(Date.now() - 300000).toLocaleString() // 5 minutes ago
        },
        {
            id: 3,
            userImage: 'results/user_3.jpg',
            clothImage: 'results/cloth_3.jpg',
            resultImage: 'results/combined_3.jpg',
            confidence: 92,
            processingTime: '2.1 seconds',
            resolution: '640x480',
            timestamp: new Date(Date.now() - 600000).toLocaleString() // 10 minutes ago
        }
    ];
    
    totalResults = availableResults.length;
    console.log(`📊 Found ${totalResults} result sets`);
}

function updateNavigation() {
    const resultCounter = document.getElementById('resultCounter');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    // Update counter
    resultCounter.textContent = `Result ${currentResultIndex} of ${totalResults}`;
    
    // Update button states
    prevBtn.disabled = currentResultIndex <= 1;
    nextBtn.disabled = currentResultIndex >= totalResults;
    
    console.log(`🧭 Navigation updated - showing result ${currentResultIndex}/${totalResults}`);
}

function updateResultDisplay() {
    const currentResult = availableResults[currentResultIndex - 1];
    
    if (!currentResult) {
        console.error('❌ No result found for index:', currentResultIndex);
        showErrorState();
        return;
    }
    
    // Update images
    updateImages(currentResult);
    
    // Update details
    updateDetails(currentResult);
    
    console.log(`🖼️ Displaying result ${currentResult.id}`);
}

function updateImages(result) {
    const userImage = document.getElementById('userImage');
    const clothImage = document.getElementById('clothImage');
    const resultImage = document.getElementById('resultImage');
    const confidenceScore = document.getElementById('confidenceScore');
    
    // Update image sources with error handling
    updateImageWithFallback(userImage, result.userImage, 'blue_shirt.png');
    updateImageWithFallback(clothImage, result.clothImage, 'red_tshirt.png');
    updateImageWithFallback(resultImage, result.resultImage, 'green_striped.png');
    
    // Update confidence score
    confidenceScore.innerHTML = `<i class="fas fa-star"></i> ${result.confidence}% Match`;
    
    // Add loading animation
    [userImage, clothImage, resultImage].forEach(img => {
        img.classList.add('loading');
        img.onload = () => img.classList.remove('loading');
    });
}

function updateImageWithFallback(imgElement, src, fallbackSrc) {
    imgElement.onerror = () => {
        console.log(`⚠️ Failed to load ${src}, using fallback`);
        imgElement.src = fallbackSrc;
        imgElement.onerror = null; // Prevent infinite loop
    };
    imgElement.src = src;
}

function updateDetails(result) {
    const processingTime = document.getElementById('processingTime');
    const resolution = document.getElementById('resolution');
    const timestamp = document.getElementById('timestamp');
    
    processingTime.textContent = result.processingTime;
    resolution.textContent = result.resolution;
    timestamp.textContent = result.timestamp;
}

function showErrorState() {
    const imagesContainer = document.querySelector('.images-container');
    imagesContainer.innerHTML = `
        <div class="error-state">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>No Results Found</h3>
            <p>No virtual try-on results are available in the results folder.</p>
            <button class="retry-btn" onclick="loadResults(); updateResultDisplay();">
                <i class="fas fa-sync-alt"></i> Refresh
            </button>
        </div>
    `;
}

// Navigation functions
function previousResult() {
    if (currentResultIndex > 1) {
        currentResultIndex--;
        updateNavigation();
        updateResultDisplay();
        
        // Add transition effect
        addTransitionEffect('slide-right');
        
        showNotification(`📷 Viewing result ${currentResultIndex}`, 'info');
    }
}

function nextResult() {
    if (currentResultIndex < totalResults) {
        currentResultIndex++;
        updateNavigation();
        updateResultDisplay();
        
        // Add transition effect
        addTransitionEffect('slide-left');
        
        showNotification(`📷 Viewing result ${currentResultIndex}`, 'info');
    }
}

function addTransitionEffect(direction) {
    const imagesContainer = document.querySelector('.images-container');
    imagesContainer.classList.add('transitioning', direction);
    
    setTimeout(() => {
        imagesContainer.classList.remove('transitioning', direction);
    }, 300);
}

// Action functions
function saveResult() {
    const currentResult = availableResults[currentResultIndex - 1];
    
    showNotification('💾 Preparing download...', 'info');
    
    // Simulate save process
    setTimeout(() => {
        // In a real implementation, this would download the result image
        const link = document.createElement('a');
        link.href = currentResult.resultImage;
        link.download = `virtual-tryon-result-${currentResult.id}.jpg`;
        link.click();
        
        showNotification('✅ Result saved successfully!', 'success');
    }, 1000);
}

function compareResults() {
    showNotification('🔄 Opening comparison view...', 'info');
    
    // Create comparison modal
    createComparisonModal();
    
    showNotification('👀 Comparison view opened', 'success');
}

function createComparisonModal() {
    const modal = document.createElement('div');
    modal.className = 'comparison-modal';
    modal.innerHTML = `
        <div class="comparison-content">
            <div class="comparison-header">
                <h3>📊 Results Comparison</h3>
                <button class="close-comparison" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="comparison-grid">
                ${availableResults.map(result => `
                    <div class="comparison-item ${result.id === currentResultIndex ? 'active' : ''}">
                        <img src="${result.resultImage}" alt="Result ${result.id}" onerror="this.src='green_striped.png'">
                        <div class="comparison-info">
                            <strong>Result ${result.id}</strong>
                            <span>${result.confidence}% Match</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function shareResult() {
    const currentResult = availableResults[currentResultIndex - 1];
    
    showNotification('📤 Preparing to share...', 'info');
    
    if (navigator.share) {
        navigator.share({
            title: 'Virtual Try-On Result',
            text: `Check out my virtual try-on with ${currentResult.confidence}% match!`,
            url: window.location.href
        }).then(() => {
            showNotification('📱 Shared successfully!', 'success');
        }).catch(() => {
            fallbackShare();
        });
    } else {
        fallbackShare();
    }
}

function fallbackShare() {
    const shareUrl = window.location.href;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl).then(() => {
            showNotification('📋 Link copied to clipboard!', 'success');
        });
    } else {
        showNotification('📱 Share feature not available', 'warning');
    }
}

function regenerateResult() {
    const currentResult = availableResults[currentResultIndex - 1];
    
    showNotification('🔄 Regenerating result...', 'info');
    showLoadingOverlay('Regenerating with improved AI model...');
    
    // Simulate regeneration process
    setTimeout(() => {
        // Update confidence score randomly
        const newConfidence = Math.floor(Math.random() * 10) + 90; // 90-99%
        currentResult.confidence = newConfidence;
        currentResult.processingTime = (Math.random() * 2 + 1).toFixed(1) + ' seconds';
        currentResult.timestamp = new Date().toLocaleString();
        
        updateResultDisplay();
        hideLoadingOverlay();
        showNotification(`✨ Result regenerated with ${newConfidence}% match!`, 'success');
    }, 3000);
}

// Utility functions
function showLoadingOverlay(text = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    
    loadingText.textContent = text;
    overlay.style.display = 'flex';
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'none';
}

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

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    switch(e.key) {
        case 'ArrowLeft':
            e.preventDefault();
            previousResult();
            break;
        case 'ArrowRight':
            e.preventDefault();
            nextResult();
            break;
        case 'r':
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                loadResults();
                updateResultDisplay();
                showNotification('🔄 Results refreshed', 'info');
            }
            break;
        case 's':
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                saveResult();
            }
            break;
    }
});

// Add CSS for transitions and comparison modal
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
    
    .transitioning {
        transition: transform 0.3s ease-out;
    }
    
    .slide-left {
        transform: translateX(-10px);
    }
    
    .slide-right {
        transform: translateX(10px);
    }
    
    .loading {
        opacity: 0.7;
        filter: blur(1px);
        transition: all 0.3s;
    }
    
    .comparison-modal {
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
    
    .comparison-content {
        background: white;
        border-radius: 15px;
        padding: 20px;
        max-width: 800px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
    }
    
    .comparison-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #eee;
    }
    
    .comparison-header h3 {
        color: #8B2686;
        margin: 0;
    }
    
    .close-comparison {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
    }
    
    .comparison-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
    }
    
    .comparison-item {
        border: 2px solid transparent;
        border-radius: 10px;
        overflow: hidden;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .comparison-item.active {
        border-color: #8B2686;
        box-shadow: 0 0 15px rgba(139, 38, 134, 0.3);
    }
    
    .comparison-item img {
        width: 100%;
        height: 150px;
        object-fit: cover;
    }
    
    .comparison-info {
        padding: 10px;
        text-align: center;
        background: #f8f9fa;
    }
    
    .comparison-info strong {
        display: block;
        color: #8B2686;
        margin-bottom: 5px;
    }
    
    .comparison-info span {
        color: #666;
        font-size: 12px;
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
`;
document.head.appendChild(style); 