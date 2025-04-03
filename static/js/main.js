document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Dark mode functionality
    function initDarkMode() {
        // Create dark mode toggle button
        const darkModeToggle = document.createElement('button');
        darkModeToggle.classList.add('dark-mode-toggle');
        darkModeToggle.setAttribute('aria-label', 'Toggle dark mode');
        darkModeToggle.innerHTML = '<i class="fas fa-moon"></i><i class="fas fa-sun"></i>';
        document.body.appendChild(darkModeToggle);
        
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
        
        // Toggle dark mode on click
        darkModeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const themeColorMeta = document.getElementById('theme-color-meta');
            
            if (currentTheme === 'dark') {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                if (themeColorMeta) themeColorMeta.setAttribute('content', '#007bff');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if (themeColorMeta) themeColorMeta.setAttribute('content', '#121212');
            }
        });
    }
    
    // Initialize dark mode
    initDarkMode();
    
    // Navbar hide on scroll
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down & past the threshold
            navbar.classList.add('navbar-hidden');
        } else {
            // Scrolling up
            navbar.classList.remove('navbar-hidden');
        }
        
        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // For Mobile or negative scrolling
    }, false);

    // Add fade-in animation to elements
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        });

        observer.observe(element);
    });

    // Payment method selection
    const paymentMethods = document.querySelectorAll('.payment-method-card');
    if (paymentMethods.length > 0) {
        paymentMethods.forEach(method => {
            method.addEventListener('click', function() {
                // Remove selected class from all methods
                paymentMethods.forEach(m => m.classList.remove('selected'));
                
                // Add selected class to clicked method
                this.classList.add('selected');
                
                // Set the value in the hidden input
                const methodValue = this.dataset.method;
                document.getElementById('payment_method').value = methodValue;
            });
        });
    }

    // Appointment date picker functionality
    const appointmentDateInput = document.getElementById('appointment_date');
    if (appointmentDateInput) {
        // Set min date to today
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(today.getDate() + 1);
        
        const formattedTomorrow = tomorrow.toISOString().split('T')[0];
        appointmentDateInput.setAttribute('min', formattedTomorrow);
        
        // Handle date selection to fetch available time slots
        appointmentDateInput.addEventListener('change', function() {
            fetchAvailableTimeSlots(this.value);
        });
    }

    // Time slot selection
    const timeSlotsContainer = document.getElementById('time-slots-container');
    if (timeSlotsContainer) {
        timeSlotsContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('time-slot') && !e.target.classList.contains('disabled')) {
                // Remove selected class from all time slots
                document.querySelectorAll('.time-slot').forEach(slot => {
                    slot.classList.remove('selected');
                });
                
                // Add selected class to clicked time slot
                e.target.classList.add('selected');
                
                // Set the value in the hidden input
                const timeValue = e.target.dataset.time;
                document.getElementById('appointment_time').value = timeValue;
            }
        });
    }

    // Interactive star rating
    const starContainer = document.querySelector('.star-rating');
    const ratingInput = document.querySelector('.rating-input');

    if (starContainer && ratingInput) {
        const stars = starContainer.querySelectorAll('.star-btn');
        const ratingFeedback = document.querySelector('.rating-feedback span');

        const ratingTexts = {
            1: 'Poor',
            2: 'Fair',
            3: 'Good',
            4: 'Very Good',
            5: 'Excellent'
        };

        function updateStars(rating, isHover) {
            stars.forEach((star, index) => {
                const icon = star.querySelector('i');
                if (index < rating) {
                    icon.className = 'fas fa-star text-warning';
                } else {
                    icon.className = 'far fa-star text-warning';
                }
            });

            if (ratingFeedback && rating > 0) {
                ratingFeedback.textContent = ratingTexts[rating] || 'Click to rate';
            }
        }

        // Hover effect
        stars.forEach(star => {
            star.addEventListener('mouseover', function() {
                const rating = this.dataset.rating;
                updateStars(rating, true);
            });
        });

        // Mouse leave - reset to selected rating
        starContainer.addEventListener('mouseleave', function() {
            const rating = ratingInput.value || 0;
            updateStars(rating, false);
        });

        // Click to set rating
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = this.dataset.rating;
                ratingInput.value = rating;
                updateStars(rating, false);
            });
        });
    }

    // Handle form submissions with validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            let formValid = form.checkValidity();
            
            // Check if this is a review form with star rating
            const ratingInput = form.querySelector('.rating-input');
            const ratingError = document.getElementById('rating-error');
            
            if (ratingInput && (!ratingInput.value || ratingInput.value === "0")) {
                // Special validation for star rating
                formValid = false;
                if (ratingError) {
                    ratingError.style.display = 'block !important';
                    ratingError.style.removeProperty('display');
                }
                
                // Highlight the star rating area
                const starRating = form.querySelector('.star-rating');
                if (starRating) {
                    starRating.classList.add('was-validated');
                    
                    // Add a pulse animation to draw attention
                    starRating.style.animation = 'none';
                    void starRating.offsetWidth; // Trigger reflow
                    starRating.style.animation = 'attention-pulse 0.8s ease';
                }
            }
            
            if (!formValid) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                // Show loader on valid form submission
                const loader = document.querySelector('.loader');
                if (loader) {
                    loader.style.display = 'block';
                }
            }
            
            form.classList.add('was-validated');
        }, false);
    });
});

// Function to fetch available time slots
function fetchAvailableTimeSlots(date) {
    const timeSlotsContainer = document.getElementById('time-slots-container');
    const loader = document.querySelector('.time-slots-loader');
    
    if (timeSlotsContainer && loader) {
        // Show loader
        loader.style.display = 'block';
        timeSlotsContainer.innerHTML = '';
        
        // Fetch available slots from API
        fetch(`/api/available-slots?date=${date}`)
            .then(response => response.json())
            .then(data => {
                // Hide loader
                loader.style.display = 'none';
                
                // Clear any existing time slots
                timeSlotsContainer.innerHTML = '';
                
                // Check if there are available slots
                if (data.length === 0) {
                    timeSlotsContainer.innerHTML = '<p class="text-danger">No available slots for this date. Please select another date.</p>';
                    return;
                }
                
                // Create a new div for the time slots
                const timeSlots = document.createElement('div');
                timeSlots.className = 'time-slots';
                
                // Add each available time slot
                data.forEach(slot => {
                    const timeSlot = document.createElement('div');
                    timeSlot.className = 'time-slot';
                    timeSlot.dataset.time = slot;
                    timeSlot.textContent = formatTimeSlot(slot);
                    timeSlots.appendChild(timeSlot);
                });
                
                timeSlotsContainer.appendChild(timeSlots);
            })
            .catch(error => {
                // Hide loader and show error message
                loader.style.display = 'none';
                timeSlotsContainer.innerHTML = `<p class="text-danger">Error loading time slots: ${error.message}</p>`;
            });
    }
}

// Helper function to format time slot from 24-hour to 12-hour format
function formatTimeSlot(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours, 10);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}:${minutes} ${ampm}`;
}
