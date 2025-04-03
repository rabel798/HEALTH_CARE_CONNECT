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

    // Enhanced Interactive star rating
    const starContainers = document.querySelectorAll('.star-rating');
    
    starContainers.forEach(starContainer => {
        const ratingInput = starContainer.querySelector('.rating-input') || 
                          document.querySelector('input[name="rating"]');
        
        if (ratingInput) {
            const stars = starContainer.querySelectorAll('.star-btn');
            
            // Add active class to container for hover effects
            starContainer.classList.add('active');
            
            // Initialize with any existing rating
            if (ratingInput.value) {
                updateStars(ratingInput.value);
            }
            
            // Hover effect - highlight stars up to the current hover position
            stars.forEach((star, index) => {
                star.addEventListener('mouseover', function() {
                    // Highlight all stars up to this one
                    highlightStars(index + 1);
                });
            });
            
            // Mouse leave - reset to selected rating
            starContainer.addEventListener('mouseleave', function() {
                const rating = ratingInput.value || 0;
                updateStars(rating);
            });
            
            // Click to set rating
            stars.forEach((star, index) => {
                star.addEventListener('click', function() {
                    const rating = index + 1; // Set rating based on star position (1-5)
                    ratingInput.value = rating;
                    updateStars(rating);
                    
                    // Update rating feedback text if it exists
                    const ratingFeedback = starContainer.closest('div').querySelector('.rating-feedback');
                    if (ratingFeedback) {
                        const feedbackMessages = [
                            'Poor',
                            'Fair',
                            'Good',
                            'Very Good',
                            'Excellent'
                        ];
                        
                        // Update the feedback text with selected rating
                        const feedbackText = feedbackMessages[rating - 1];
                        ratingFeedback.innerHTML = `<span class="badge bg-primary px-3 py-2 rounded-pill">You rated: ${feedbackText} (${rating} ${rating === 1 ? 'star' : 'stars'})</span>`;
                        
                        // Hide any error message
                        const ratingError = document.getElementById('rating-error');
                        if (ratingError) {
                            ratingError.style.display = 'none !important';
                        }
                    }
                    
                    // Add pulse animation to selected stars
                    stars.forEach((s, i) => {
                        if (i < rating) {
                            // Remove and re-add the animation to restart it
                            s.classList.remove('selected');
                            void s.offsetWidth; // Force reflow
                            s.classList.add('selected');
                        }
                    });
                });
            });
            
            // Highlight stars on hover (temporary)
            function highlightStars(rating) {
                stars.forEach((star, index) => {
                    // Remove selected class to prevent conflicts
                    star.classList.remove('selected');
                    
                    // Update icon based on hover position
                    if (index < rating) {
                        star.className = 'fas fa-star star-btn text-warning';
                    } else {
                        star.className = 'far fa-star star-btn text-warning';
                    }
                });
            }
            
            // Update stars permanently when a rating is selected
            function updateStars(rating) {
                stars.forEach((star, index) => {
                    if (index < rating) {
                        star.className = 'fas fa-star star-btn text-warning selected';
                    } else {
                        star.className = 'far fa-star star-btn text-warning';
                    }
                });
            }
        }
    });

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
