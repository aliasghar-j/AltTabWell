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
    if (foodImageInput) {
        foodImageInput.addEventListener('change', function(event) {
            // Could add image preview functionality here
            console.log('File selected:', event.target.files[0]?.name);
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
}