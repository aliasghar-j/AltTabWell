// Main JavaScript file for Corporate Wellness application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any components that need JavaScript
    initializeNavbar();
    
    // Add event listeners for any interactive elements
    addEventListeners();
});

function initializeNavbar() {
    // Highlight active nav item based on current page
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
}

function addEventListeners() {
    // Example: File upload preview
    const foodImageInput = document.getElementById('food_image');
    const imagePreview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    
    if (foodImageInput) {
        foodImageInput.addEventListener('change', function(event) {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    imagePreview.classList.remove('d-none');
                }
                
                reader.readAsDataURL(this.files[0]);
            } else {
                imagePreview.classList.add('d-none');
            }
        });
    }
    
    // Example: Step counter update button
    const updateStepsBtn = document.querySelector('.btn-outline-primary');
    if (updateStepsBtn) {
        updateStepsBtn.addEventListener('click', function() {
            // This would be replaced with actual API call in production
            const randomSteps = Math.floor(Math.random() * 10000);
            const stepsDisplay = document.querySelector('.card-body h5 .text-primary');
            if (stepsDisplay) {
                stepsDisplay.textContent = randomSteps.toLocaleString();
            }
            
            // Update progress bar
            const progressPercent = Math.min(100, Math.floor(randomSteps / 100));
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${progressPercent}%`;
                progressBar.setAttribute('aria-valuenow', progressPercent);
                progressBar.textContent = `${progressPercent}%`;
            }
        });
    }
    
    // Food calorie lookup functionality
    const lookupCaloriesBtn = document.getElementById('lookupCaloriesBtn');
    const foodNameInput = document.getElementById('foodNameInput');
    const calorieResult = document.getElementById('calorieResult');
    const addFoodForm = document.getElementById('addFoodForm');
    const foodNameField = document.getElementById('food_name');
    const caloriesField = document.getElementById('calories');
    
    if (lookupCaloriesBtn && foodNameInput && calorieResult) {
        lookupCaloriesBtn.addEventListener('click', function() {
            const foodName = foodNameInput.value.trim();
            
            if (!foodName) {
                showCalorieResult('Please enter a food name', 'warning');
                return;
            }
            
            // Show loading state
            lookupCaloriesBtn.disabled = true;
            lookupCaloriesBtn.textContent = 'Looking up...';
            showCalorieResult('Searching for calorie information...', 'info');
            
            // Make API call to Gemini
            fetch(`/api/gemini/search?foodName=${encodeURIComponent(foodName)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show the calorie result
                        showCalorieResult(data.description, 'success');
                        
                        // Populate the hidden form and submit it
                        if (addFoodForm && foodNameField && caloriesField) {
                            foodNameField.value = data.food_name;
                            caloriesField.value = data.calories;
                            addFoodForm.submit();
                        }
                    } else {
                        showCalorieResult(data.error || 'No calorie information found', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showCalorieResult('Failed to lookup calories. Please try again.', 'danger');
                })
                .finally(() => {
                    // Reset button state
                    lookupCaloriesBtn.disabled = false;
                    lookupCaloriesBtn.textContent = 'Add';
                });
        });
        
        // Allow Enter key to trigger lookup
        foodNameInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                lookupCaloriesBtn.click();
            }
        });
    }
}

function showCalorieResult(message, type) {
    const calorieResult = document.getElementById('calorieResult');
    if (calorieResult) {
        calorieResult.className = `alert alert-${type}`;
        calorieResult.textContent = message;
        calorieResult.style.display = 'block';
        
        // Auto-hide after 5 seconds for success messages
        if (type === 'success') {
            setTimeout(() => {
                calorieResult.style.display = 'none';
            }, 5000);
        }
    }
}