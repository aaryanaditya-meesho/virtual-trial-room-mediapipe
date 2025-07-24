// Virtual Try-On App JavaScript

// DOM Elements
const modal = document.getElementById('tryOnModal');
const navItems = document.querySelectorAll('.nav-item');
const categoryItems = document.querySelectorAll('.category-item');
const searchInput = document.querySelector('.search-bar input');
const productCards = document.querySelectorAll('.product-card');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    addEventListeners();
    animateOnLoad();
});

// Initialize app
function initializeApp() {
    console.log('🎽 Virtual Try-On App Initialized');
    
    // Set default active state
    updateActiveNav('home');
    
    // Add smooth scrolling
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Check if user is on mobile
    if (isMobile()) {
        console.log('📱 Mobile device detected');
        adaptForMobile();
    }
}

// Add event listeners
function addEventListeners() {
    // Search functionality
    searchInput.addEventListener('focus', handleSearchFocus);
    searchInput.addEventListener('blur', handleSearchBlur);
    searchInput.addEventListener('input', handleSearchInput);
    
    // Category interactions
    categoryItems.forEach(item => {
        item.addEventListener('click', handleCategoryClick);
    });
    
    // Product card interactions
    productCards.forEach(card => {
        card.addEventListener('click', handleProductClick);
    });
    
    // Bottom navigation
    navItems.forEach(item => {
        item.addEventListener('click', handleNavClick);
    });
    
    // Modal interactions
    window.addEventListener('click', handleModalOutsideClick);
    
    // Escape key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
    });
    
    // Swipe gestures for mobile
    if (isMobile()) {
        addSwipeGestures();
    }
}

// Animation on load
function animateOnLoad() {
    // Stagger animation for category items
    categoryItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.5s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Animate product cards
    productCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'scale(0.8)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'scale(1)';
        }, 500 + (index * 150));
    });
}

// Virtual Try-On Functions
function openCatalog() {
    showNotification('👗 Opening Virtual Tailor Catalog...', 'info');
    
    // Open catalog page
    window.open('catalog.html', '_blank');
    
    showNotification('✨ Catalog opened! Choose your fabric', 'success');
    
    trackEvent('virtual_tailor_catalog_opened');
}

function openVirtualTryOn() {
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Add analytics
    trackEvent('virtual_tryon_opened');
    
    // Add sound effect (optional)
    playClickSound();
}

function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
    
    trackEvent('virtual_tryon_closed');
}

function startBasicTryOn() {
    showNotification('👗 Opening Virtual Try-On Studio...', 'info');
    
    closeModal();
    
    // Open the new virtual try-on page
    window.open('virtual-tryon.html', '_blank');
    
    showNotification('✨ Virtual Try-On Studio opened!', 'success');
    
    trackEvent('virtual_tryon_studio_opened');
}

function startAdvancedTryOn() {
    showNotification('✨ Starting Advanced Trial Room...', 'info');
    
    closeModal();
    
    try {
        // Launch advanced_trial_room.py directly
        const scriptPath = window.location.href.replace('/virtual-try-on-app/index.html', '/advanced_trial_room.py');
        window.open(scriptPath, '_blank');
        
        showNotification('🚀 Launching advanced trial room...', 'success');
        
        // Backup: Show terminal command
        setTimeout(() => {
            const terminalCommand = 'python3 advanced_trial_room.py';
            if (navigator.clipboard) {
                navigator.clipboard.writeText(terminalCommand).then(() => {
                    showNotification('📋 Command copied! Paste in Terminal if app didn\'t open', 'info');
                }).catch(() => {
                    showNotification('💻 Run in Terminal: python3 advanced_trial_room.py', 'info');
                });
            }
        }, 2000);
        
    } catch (error) {
        showNotification('💻 Please run: python3 advanced_trial_room.py', 'warning');
    }
    
    trackEvent('advanced_trial_room_launched');
}

function viewMeasurements() {
    showNotification('📐 Executing Body Measurement Tool...', 'info');
    
    closeModal();
    
    // Try multiple methods to actually RUN the Python script
    executeShoulderDistance();
    
    trackEvent('shoulder_distance_executed');
}

function executeShoulderDistance() {
    // Method 1: Try to execute shell script (Mac/Linux)
    try {
        const shellScript = window.location.href.replace('/virtual-try-on-app/index.html', '/run_shoulder_distance.sh');
        window.open(shellScript, '_blank');
        showNotification('🚀 Executing shoulder measurement script...', 'success');
    } catch (error) {
        console.log('Shell script method failed, trying alternatives...');
    }
    
    // Method 2: Try Windows batch file
    setTimeout(() => {
        try {
            const batScript = window.location.href.replace('/virtual-try-on-app/index.html', '/run_shoulder_distance.bat');
            window.open(batScript, '_blank');
        } catch (error) {
            console.log('Batch file method failed');
        }
    }, 500);
    
    // Method 3: Try Python protocol (if registered)
    setTimeout(() => {
        try {
            window.location.href = 'python://shoulder_distance.py';
        } catch (error) {
            console.log('Python protocol not available');
        }
    }, 1000);
    
    // Method 4: Auto-copy command and show instructions
    setTimeout(() => {
        const command = 'python3 shoulder_distance.py';
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(command).then(() => {
                showNotification('📋 Command copied to clipboard! Paste in Terminal to run', 'success');
                
                // Show detailed execution instructions
                setTimeout(() => {
                    showExecutionInstructions();
                }, 1000);
                
            }).catch(() => {
                showExecutionInstructions();
            });
        } else {
            showExecutionInstructions();
        }
    }, 1500);
}

function showExecutionInstructions() {
    const instructions = `
    🚀 TO RUN SHOULDER MEASUREMENT TOOL:
    
    Option 1 (Recommended):
    • Open Terminal/Command Prompt
    • Navigate to your project folder
    • Run: python3 shoulder_distance.py
    
    Option 2:
    • Double-click run_shoulder_distance.sh (Mac/Linux)
    • Or double-click run_shoulder_distance.bat (Windows)
    
    Option 3:
    • Open Finder/File Explorer
    • Right-click shoulder_distance.py
    • Choose "Open with Python"
    `;
    
    alert(instructions);
    showNotification('💡 Check the popup for execution instructions!', 'info');
}



// Search functionality
function handleSearchFocus() {
    searchInput.parentElement.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.3)';
    searchInput.parentElement.style.border = '2px solid #667eea';
}

function handleSearchBlur() {
    searchInput.parentElement.style.boxShadow = 'none';
    searchInput.parentElement.style.border = 'none';
}

function handleSearchInput(e) {
    const query = e.target.value.toLowerCase();
    
    if (query.length > 2) {
        // Simulate search results
        showNotification(`🔍 Searching for "${query}"...`, 'info');
        
        // In a real app, this would filter products
        // filterProducts(query);
    }
}

// Category interactions
function handleCategoryClick(e) {
    const category = e.currentTarget;
    const categoryName = category.querySelector('span').textContent;
    
    // Add selection animation
    category.style.transform = 'scale(0.95)';
    setTimeout(() => {
        category.style.transform = 'scale(1)';
    }, 150);
    
    showNotification(`📂 Loading ${categoryName}...`, 'info');
    
    // If it's clothing category, show try-on option
    if (['Western Wear', 'Kurtis & Dresses', 'Men Fashion', 'Sarees'].includes(categoryName)) {
        setTimeout(() => {
            showNotification('✂️ Virtual Tailor available for this category!', 'success');
        }, 1000);
    }
    
    trackEvent('category_clicked', { category: categoryName });
}

// Product interactions
function handleProductClick(e) {
    const product = e.currentTarget;
    const productName = product.querySelector('p').textContent;
    
    // Add click animation
    product.style.transform = 'scale(0.95)';
    setTimeout(() => {
        product.style.transform = 'scale(1)';
    }, 150);
    
    showNotification(`🛍️ ${productName} - Try with Virtual Tailor?`, 'info');
    
    // Show quick try-on option
    setTimeout(() => {
        if (confirm('Experience perfect fitting with our AI Virtual Tailor?')) {
            openVirtualTryOn();
        }
    }, 500);
    
    trackEvent('product_clicked', { product: productName });
}

// Navigation handling
function handleNavClick(e) {
    const navItem = e.currentTarget;
    const navName = navItem.querySelector('span').textContent.toLowerCase();
    
    // Don't handle tailor nav here (it has its own onclick)
    if (navName === 'tailor') return;
    
    updateActiveNav(navName);
    
    // Simulate navigation
    switch(navName) {
        case 'home':
            showNotification('🏠 Welcome to Home', 'success');
            break;
        case 'categories':
            showNotification('📂 Browse Categories', 'info');
            scrollToCategories();
            break;
        case 'video finds':
            showNotification('🎥 Video Finds Coming Soon!', 'info');
            break;
        case 'my orders':
            showNotification('📦 My Orders Coming Soon!', 'info');
            break;
    }
    
    trackEvent('navigation_clicked', { page: navName });
}

function updateActiveNav(activeNavName) {
    navItems.forEach(item => {
        const navName = item.querySelector('span').textContent.toLowerCase();
        if (navName === activeNavName) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Modal outside click handler
function handleModalOutsideClick(e) {
    if (e.target === modal) {
        closeModal();
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Styling
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        zIndex: '10000',
        fontSize: '14px',
        fontWeight: '500',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease'
    });
    
    // Type-specific styling
    const colors = {
        info: { bg: '#e3f2fd', text: '#1976d2', border: '#2196f3' },
        success: { bg: '#e8f5e8', text: '#2e7d32', border: '#4caf50' },
        warning: { bg: '#fff3e0', text: '#f57c00', border: '#ff9800' },
        error: { bg: '#ffebee', text: '#c62828', border: '#f44336' }
    };
    
    const color = colors[type] || colors.info;
    notification.style.backgroundColor = color.bg;
    notification.style.color = color.text;
    notification.style.borderLeft = `4px solid ${color.border}`;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function scrollToCategories() {
    const categoriesSection = document.querySelector('.categories-section');
    categoriesSection.scrollIntoView({ behavior: 'smooth' });
}

function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
           || window.innerWidth < 768;
}

function adaptForMobile() {
    // Add mobile-specific adaptations
    document.body.classList.add('mobile-device');
    
    // Reduce animation duration for performance
    const style = document.createElement('style');
    style.textContent = `
        .mobile-device * {
            transition-duration: 0.2s !important;
            animation-duration: 0.2s !important;
        }
    `;
    document.head.appendChild(style);
}

function addSwipeGestures() {
    let startX, startY, distX, distY;
    
    document.addEventListener('touchstart', e => {
        const touch = e.touches[0];
        startX = touch.clientX;
        startY = touch.clientY;
    });
    
    document.addEventListener('touchmove', e => {
        if (!startX || !startY) return;
        
        const touch = e.touches[0];
        distX = touch.clientX - startX;
        distY = touch.clientY - startY;
    });
    
    document.addEventListener('touchend', e => {
        if (!startX || !startY) return;
        
        // Horizontal swipe
        if (Math.abs(distX) > Math.abs(distY) && Math.abs(distX) > 50) {
            if (distX > 0) {
                // Swipe right
                handleSwipeRight();
            } else {
                // Swipe left
                handleSwipeLeft();
            }
        }
        
        startX = startY = distX = distY = null;
    });
}

function handleSwipeRight() {
    showNotification('👈 Swipe navigation coming soon!', 'info');
}

function handleSwipeLeft() {
    showNotification('👉 Swipe navigation coming soon!', 'info');
}

function playClickSound() {
    // Create audio context for click sound (optional)
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.1);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    } catch (e) {
        // Ignore audio errors
    }
}

function trackEvent(eventName, properties = {}) {
    // Analytics tracking (would integrate with real analytics)
    console.log(`📊 Event: ${eventName}`, properties);
    
    // In a real app, this would send to analytics service:
    // gtag('event', eventName, properties);
    // mixpanel.track(eventName, properties);
}

// Performance monitoring
function measurePerformance() {
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const perfData = performance.timing;
            const loadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`⚡ Page load time: ${loadTime}ms`);
            
            trackEvent('page_performance', {
                loadTime,
                domContentLoaded: perfData.domContentLoadedEventEnd - perfData.navigationStart
            });
        });
    }
}

// Initialize performance monitoring
measurePerformance();

// Export functions for external access
window.VirtualTryOnApp = {
    openVirtualTryOn,
    closeModal,
    startBasicTryOn,
    startAdvancedTryOn,
    viewMeasurements,
    showNotification
}; 