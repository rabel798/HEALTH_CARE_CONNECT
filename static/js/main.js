document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

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
        
        function updateStars(rating, isHover) {
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.className = 'fas fa-star text-warning star-btn';
                } else {
                    star.className = 'far fa-star text-warning star-btn';
                }
            });
        }
    }

    // Handle form submissions with validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
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
