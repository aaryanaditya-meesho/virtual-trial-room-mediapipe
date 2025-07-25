// Global variables
let selectedFabric = null;
let selectedFabricName = '';
let allFabricCards = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeCatalog();
});

function initializeCatalog() {
    console.log('🛍️ Initializing Catalog...');
    
    // Get all fabric cards for filtering
    allFabricCards = Array.from(document.querySelectorAll('.fabric-card'));
    
    // Initialize search functionality
    setupSearch();
    
    // Show all categories by default
    showCategory('all');
    
    console.log('✅ Catalog initialized');
}

// Category Management
function showCategory(category) {
    console.log(`📁 Showing category: ${category}`);
    
    // Update active category button
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-category="${category}"]`).classList.add('active');
    
    // Show/hide collection sections and fabric cards
    const collectionSections = document.querySelectorAll('.collection-section');
    const fabricCards = document.querySelectorAll('.fabric-card');
    
    if (category === 'all') {
        // Show all sections and cards
        collectionSections.forEach(section => {
            section.classList.remove('hidden');
        });
        fabricCards.forEach(card => {
            card.style.display = 'block';
        });
        
        // Hide custom upload section for 'all' category
        const customSection = document.getElementById('custom-collection');
        if (customSection) {
            customSection.style.display = 'none';
            customSection.classList.add('hidden');
        }
    } else if (category === 'custom') {
        // Hide all regular collection sections
        collectionSections.forEach(section => {
            section.classList.add('hidden');
        });
        
        // Hide all fabric cards
        fabricCards.forEach(card => {
            card.style.display = 'none';
        });
        
        // Show the custom upload section
        const customSection = document.getElementById('custom-collection');
        
        if (customSection) {
            customSection.style.display = 'block';
            customSection.classList.remove('hidden');
            console.log('✅ Custom section shown');
        } else {
            console.error('❌ Custom section not found!');
        }
    } else {
        // Show only selected category
        collectionSections.forEach(section => {
            if (section.id === `${category}-collection`) {
                section.classList.remove('hidden');
            } else {
                section.classList.add('hidden');
            }
        });
        
        // Hide custom upload section
        const customSection = document.getElementById('custom-collection');
        if (customSection) {
            customSection.style.display = 'none';
            customSection.classList.add('hidden');
        }
        
        fabricCards.forEach(card => {
            if (card.getAttribute('data-category') === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Add transition effect
    addCategoryTransition();
    
    // Re-setup favorite buttons for newly visible cards
    setTimeout(() => {
        setupFavoriteButtons();
    }, 100);
    
    showNotification(`📂 Showing ${category === 'all' ? 'all items' : category}`, 'info');
}

function addCategoryTransition() {
    const visibleCards = document.querySelectorAll('.fabric-card[style*="block"], .fabric-card:not([style*="none"])');
    
    visibleCards.forEach((card, index) => {
        card.style.animation = 'none';
        card.offsetHeight; // Trigger reflow
        card.style.animation = `fadeInUp 0.6s ease-out ${index * 0.1}s`;
    });
}

// Search Functionality
function toggleSearch() {
    const searchContainer = document.getElementById('searchContainer');
    const searchInput = document.getElementById('searchInput');
    
    if (searchContainer.style.display === 'none' || !searchContainer.style.display) {
        searchContainer.style.display = 'block';
        searchInput.focus();
        showNotification('🔍 Search activated', 'info');
    } else {
        searchContainer.style.display = 'none';
        searchInput.value = '';
        // Reset search results
        allFabricCards.forEach(card => {
            card.style.display = 'block';
        });
        showNotification('🔍 Search closed', 'info');
    }
}

function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        
        if (query === '') {
            // Show all cards when search is empty
            allFabricCards.forEach(card => {
                card.style.display = 'block';
            });
            return;
        }
        
        searchItems(query);
    });
    
    // Handle Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = e.target.value.toLowerCase().trim();
            if (query) {
                searchItems(query);
                showNotification(`🔍 Searching for "${query}"`, 'info');
            }
        }
    });
}

function searchItems(query = null) {
    if (!query) {
        const searchInput = document.getElementById('searchInput');
        query = searchInput.value.toLowerCase().trim();
    }
    
    // If query is passed directly (from suggestion tags), update search input
    if (typeof query === 'string' && query.length > 0) {
        const searchInput = document.getElementById('searchInput');
        const searchContainer = document.getElementById('searchContainer');
        
        // Make sure search is open
        if (searchContainer.style.display === 'none' || !searchContainer.style.display) {
            searchContainer.style.display = 'block';
        }
        
        searchInput.value = query;
    }
    
    let foundCount = 0;
    
    allFabricCards.forEach(card => {
        const title = card.querySelector('h4').textContent.toLowerCase();
        const fabricType = card.querySelector('.fabric-type').textContent.toLowerCase();
        const category = card.getAttribute('data-category').toLowerCase();
        
        const matches = title.includes(query) || 
                       fabricType.includes(query) || 
                       category.includes(query);
        
        if (matches) {
            card.style.display = 'block';
            foundCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show/hide sections based on search results
    const sections = document.querySelectorAll('.collection-section');
    sections.forEach(section => {
        const visibleCards = section.querySelectorAll('.fabric-card[style*="block"]');
        if (visibleCards.length === 0) {
            section.classList.add('hidden');
        } else {
            section.classList.remove('hidden');
        }
    });
    
    console.log(`🔍 Search results: ${foundCount} items found for "${query}"`);
    
    if (foundCount === 0) {
        showNotification(`😔 No items found for "${query}"`, 'warning');
    }
}

// Virtual Try-On Integration
function tryOnFabric(imageSrc, fabricName) {
    console.log(`👗 Try-on selected: ${fabricName}`);
    
    selectedFabric = imageSrc;
    selectedFabricName = fabricName;
    
    // Update modal content
    document.getElementById('selectedItemImage').src = imageSrc;
    document.getElementById('selectedItemName').textContent = fabricName;
    
    // Show try-on modal
    document.getElementById('tryonModal').style.display = 'flex';
    
    // Add entrance animation
    const modalContent = document.querySelector('.modal-content');
    modalContent.style.animation = 'modalSlideIn 0.3s ease-out';
    
    showNotification(`✨ ${fabricName} selected for try-on`, 'success');
}

function showTryOnModal() {
    console.log('🎭 Showing try-on modal for custom item');
    
    // Show try-on modal
    document.getElementById('tryonModal').style.display = 'flex';
    
    // Add animation
    const modalContent = document.querySelector('.modal-content');
    modalContent.style.animation = 'modalSlideIn 0.3s ease-out';
}

function closeTryOnModal() {
    const modal = document.getElementById('tryonModal');
    const modalContent = document.querySelector('.modal-content');
    
    // Add exit animation
    modalContent.style.animation = 'modalSlideOut 0.3s ease-out';
    
    setTimeout(() => {
        modal.style.display = 'none';
        selectedFabric = null;
        selectedFabricName = '';
    }, 300);
    
    showNotification('👋 Try-on cancelled', 'info');
}

function startTryOnWithCamera() {
    // Check if it's a custom item or regular fabric
    if (window.currentCustomItem) {
        console.log(`📸 Starting camera try-on with custom item: ${window.currentCustomItem.name}`);
        
        // Store custom item data for the virtual try-on page
        localStorage.setItem('selectedFabric', window.currentCustomItem.image);
        localStorage.setItem('selectedFabricName', window.currentCustomItem.name);
        localStorage.setItem('tryOnMode', 'camera');
        localStorage.setItem('isCustomItem', 'true');
        
        showNotification('📸 Opening camera try-on with your custom item...', 'info');
    } else if (selectedFabric) {
        console.log(`📸 Starting camera try-on with: ${selectedFabricName}`);
        
        // Store selected fabric in localStorage for the virtual try-on page
        localStorage.setItem('selectedFabric', selectedFabric);
        localStorage.setItem('selectedFabricName', selectedFabricName);
        localStorage.setItem('tryOnMode', 'camera');
        localStorage.removeItem('isCustomItem');
        
        showNotification('📸 Opening camera try-on...', 'info');
    } else {
        showNotification('❌ No fabric selected', 'error');
        return;
    }
    
    // Close modal and redirect
    closeTryOnModal();
    
    setTimeout(() => {
        window.location.href = 'virtual-tryon.html?mode=camera';
    }, 500);
}

function startTryOnWithUpload() {
    // Check if it's a custom item or regular fabric
    if (window.currentCustomItem) {
        console.log(`📁 Starting upload try-on with custom item: ${window.currentCustomItem.name}`);
        
        // Store custom item data for the virtual try-on page
        localStorage.setItem('selectedFabric', window.currentCustomItem.image);
        localStorage.setItem('selectedFabricName', window.currentCustomItem.name);
        localStorage.setItem('tryOnMode', 'upload');
        localStorage.setItem('isCustomItem', 'true');
        
        showNotification('📁 Opening upload try-on with your custom item...', 'info');
    } else if (selectedFabric) {
        console.log(`📁 Starting upload try-on with: ${selectedFabricName}`);
        
        // Store selected fabric in localStorage for the virtual try-on page
        localStorage.setItem('selectedFabric', selectedFabric);
        localStorage.setItem('selectedFabricName', selectedFabricName);
        localStorage.setItem('tryOnMode', 'upload');
        localStorage.removeItem('isCustomItem');
        
        showNotification('📁 Opening upload try-on...', 'info');
    } else {
        showNotification('❌ No fabric selected', 'error');
        return;
    }
    
    // Close modal and redirect
    closeTryOnModal();
    
    setTimeout(() => {
        window.location.href = 'virtual-tryon.html?mode=upload';
    }, 500);
}

// Utility Functions
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
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }
    }, 4000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    switch(e.key) {
        case '/':
            e.preventDefault();
            toggleSearch();
            break;
        case 'Escape':
            const modal = document.getElementById('tryonModal');
            if (modal.style.display === 'flex') {
                closeTryOnModal();
            }
            
            const searchContainer = document.getElementById('searchContainer');
            if (searchContainer.style.display === 'block') {
                toggleSearch();
            }
            break;
        case '1':
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                showCategory('all');
            }
            break;
        case '2':
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                showCategory('shirts');
            }
            break;
        case '3':
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                showCategory('salwar');
            }
            break;
    }
});

// Modal click outside to close
document.addEventListener('click', function(e) {
    const modal = document.getElementById('tryonModal');
    if (e.target === modal) {
        closeTryOnModal();
    }
});

// Smooth scrolling for category changes
function smoothScrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add CSS animations dynamically
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
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    @keyframes modalSlideIn {
        from {
            opacity: 0;
            transform: scale(0.8) translateY(50px);
        }
        to {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }
    
    @keyframes modalSlideOut {
        from {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
        to {
            opacity: 0;
            transform: scale(0.8) translateY(50px);
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
    
    .fabric-card.highlighted {
        border: 2px solid #FFD700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    }
`;
document.head.appendChild(style);

// Handle favorite button clicks
function setupFavoriteButtons() {
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            
            const icon = this.querySelector('i');
            const fabricName = this.closest('.fabric-info').querySelector('h4').textContent;
            
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                this.style.color = '#E91E63';
                showNotification(`❤️ ${fabricName} added to favorites!`, 'success');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                this.style.color = '#ddd';
                showNotification(`💔 ${fabricName} removed from favorites`, 'info');
            }
            
            // Add animation
            this.style.transform = 'scale(1.3)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);
        });
    });
}

// Custom Upload Functions
let uploadedItems = JSON.parse(localStorage.getItem('uploadedClothingItems') || '[]');

function triggerFileUpload() {
    document.getElementById('customClothingInput').click();
}

function handleCustomUpload(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showNotification('❌ Please select a valid image file', 'error');
            return;
        }
        
        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            showNotification('❌ File size must be less than 10MB', 'error');
            return;
        }
        
        showNotification('📤 Uploading your clothing...', 'info');
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const imageData = e.target.result;
            const uploadedItem = {
                id: Date.now(),
                name: file.name.replace(/\.[^/.]+$/, ""), // Remove file extension
                displayName: `Custom ${file.name.replace(/\.[^/.]+$/, "")}`,
                image: imageData,
                uploadDate: new Date().toLocaleDateString(),
                category: 'custom'
            };
            
            // Add to uploaded items
            uploadedItems.push(uploadedItem);
            localStorage.setItem('uploadedClothingItems', JSON.stringify(uploadedItems));
            
            // Update the display
            updateUploadedItemsDisplay();
            
            // Update category count
            updateCustomCategoryCount();
            
            showNotification('✅ Clothing uploaded successfully!', 'success');
            
            // Clear the input
            input.value = '';
        };
        
        reader.readAsDataURL(file);
    }
}

function updateUploadedItemsDisplay() {
    const uploadedGrid = document.getElementById('uploadedGrid');
    const uploadedItemsSection = document.getElementById('uploadedItemsGrid');
    
    if (uploadedItems.length === 0) {
        uploadedItemsSection.style.display = 'none';
        return;
    }
    
    uploadedItemsSection.style.display = 'block';
    uploadedGrid.innerHTML = '';
    
    uploadedItems.forEach(item => {
        const itemCard = document.createElement('div');
        itemCard.className = 'fabric-card uploaded-item';
        itemCard.innerHTML = `
            <div class="fabric-image">
                <img src="${item.image}" alt="${item.displayName}">
                <div class="fabric-overlay">
                    <div class="overlay-content">
                        <button class="try-on-btn" onclick="tryOnCustomItem('${item.id}')">
                            <i class="fas fa-magic"></i> Try On Now
                        </button>
                        <button class="delete-btn" onclick="deleteUploadedItem('${item.id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
                <div class="fabric-badge custom-badge">
                    <i class="fas fa-user"></i> Custom
                </div>
            </div>
            <div class="fabric-info">
                <div class="fabric-header">
                    <h4>${item.displayName}</h4>
                    <div class="upload-date">
                        <small><i class="fas fa-calendar"></i> ${item.uploadDate}</small>
                    </div>
                </div>
                <p class="fabric-type">Your Upload • Custom Design</p>
                <div class="fabric-features">
                    <span class="feature"><i class="fas fa-check"></i> AI Ready</span>
                    <span class="feature"><i class="fas fa-check"></i> High Quality</span>
                </div>
            </div>
        `;
        
        uploadedGrid.appendChild(itemCard);
    });
}

function updateCustomCategoryCount() {
    const customBtn = document.querySelector('[data-category="custom"] .category-count');
    if (customBtn) {
        if (uploadedItems.length > 0) {
            customBtn.innerHTML = uploadedItems.length;
        } else {
            customBtn.innerHTML = '<i class="fas fa-plus"></i>';
        }
    }
}

function tryOnCustomItem(itemId) {
    const item = uploadedItems.find(i => i.id == itemId);
    if (item) {
        // Use the existing try-on flow but with custom item data
        showTryOnModal();
        document.getElementById('selectedItemImage').src = item.image;
        document.getElementById('selectedItemName').textContent = item.displayName;
        
        // Store the custom item data for try-on (pass the base64 data URL directly)
        window.currentCustomItem = {
            name: item.displayName,
            image: item.image,
            isCustom: true
        };
    }
}

function deleteUploadedItem(itemId) {
    if (confirm('Are you sure you want to delete this uploaded item?')) {
        uploadedItems = uploadedItems.filter(item => item.id != itemId);
        localStorage.setItem('uploadedClothingItems', JSON.stringify(uploadedItems));
        updateUploadedItemsDisplay();
        updateCustomCategoryCount();
        showNotification('🗑️ Item deleted successfully', 'info');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        background: ${type === 'error' ? '#ff4444' : type === 'success' ? '#44ff44' : '#4444ff'};
        color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        max-width: 350px;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}



// Initialize on page load
window.addEventListener('load', function() {
    console.log('🎉 Catalog page fully loaded');
    
    // Setup interactive elements
    setupFavoriteButtons();
    
    // Initialize custom upload features
    updateUploadedItemsDisplay();
    updateCustomCategoryCount();
    
    // Check if there's a selected category from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const category = urlParams.get('category');
    
    if (category && ['all', 'shirts', 'salwar', 'kurtas', 'sarees', 'custom'].includes(category)) {
        showCategory(category);
    }
    
    // Pre-load fabric if coming from another page
    const preSelectedFabric = localStorage.getItem('catalogFabric');
    if (preSelectedFabric) {
        const fabricName = localStorage.getItem('catalogFabricName') || 'Selected Item';
        tryOnFabric(preSelectedFabric, fabricName);
        
        // Clear the stored values
        localStorage.removeItem('catalogFabric');
        localStorage.removeItem('catalogFabricName');
    }
}); 