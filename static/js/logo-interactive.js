document.addEventListener('DOMContentLoaded', function() {
    // Check if we have an SVG logo with the right ID
    const logoContainer = document.getElementById('interactive-logo-container');
    if (!logoContainer) return;
    
    // Load the SVG file
    fetch('/static/img/logo-interactive.svg')
        .then(response => response.text())
        .then(svgData => {
            // Insert the SVG content
            logoContainer.innerHTML = svgData;
            
            // Get the SVG document
            const svgElement = logoContainer.querySelector('svg');
            
            // Make sure SVG scripts run
            // The scripts in the SVG should handle mouse tracking, blinking, etc.
            // But we need to manually initialize some behaviors since the SVG is loaded dynamically
            
            const eye = svgElement.getElementById('eye');
            const pupil = svgElement.getElementById('pupil');
            const reflectionDot = svgElement.getElementById('reflectionDot');
            const topEyelid = svgElement.getElementById('topEyelid');
            const bottomEyelid = svgElement.getElementById('bottomEyelid');
            const light = svgElement.getElementById('light');
            
            if (!eye || !pupil || !reflectionDot || !topEyelid || !bottomEyelid || !light) {
                console.error('SVG elements not found');
                return;
            }
            
            // Handle mouse movement
            document.addEventListener('mousemove', function(evt) {
                // Calculate mouse position relative to the SVG
                const rect = svgElement.getBoundingClientRect();
                const mouseX = evt.clientX - rect.left;
                const mouseY = evt.clientY - rect.top;
                
                // Update light position for reflection effect
                light.setAttribute('x', mouseX);
                light.setAttribute('y', mouseY);
                
                // Move pupil slightly to follow mouse (limit movement)
                const eyeCenterX = 40;
                const eyeCenterY = 30;
                
                // Calculate direction vector from eye center to mouse
                let dx = mouseX - eyeCenterX;
                let dy = mouseY - eyeCenterY;
                
                // Limit movement to 3 units in any direction
                const maxMove = 3;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist > maxMove) {
                    dx = dx * maxMove / dist;
                    dy = dy * maxMove / dist;
                }
                
                // Apply movement to pupil
                pupil.setAttribute('cx', eyeCenterX + dx);
                
                // Move reflection dot opposite to pupil movement
                reflectionDot.setAttribute('cx', 43 - dx/2);
                reflectionDot.setAttribute('cy', 27 - dy/2);
            });
            
            // Function to make the eye blink
            function blinkEye() {
                // Show eyelids
                topEyelid.style.display = 'block';
                bottomEyelid.style.display = 'block';
                
                // Hide pupil and reflection during blink
                pupil.style.display = 'none';
                reflectionDot.style.display = 'none';
                
                // Open eye after short delay
                setTimeout(() => {
                    topEyelid.style.display = 'none';
                    bottomEyelid.style.display = 'none';
                    pupil.style.display = 'block';
                    reflectionDot.style.display = 'block';
                }, 150);
            }
            
            // Blink when mouse enters the eye
            eye.addEventListener('mouseenter', blinkEye);
            
            // Set up random blinking
            setInterval(() => {
                if (Math.random() < 0.3) { // 30% chance to blink every 3 seconds
                    blinkEye();
                }
            }, 3000);
            
            // Add click handler if the logo should be clickable
            svgElement.addEventListener('click', function() {
                // If the logo should link to the homepage or admin login
                // Redirect or trigger modal as needed
                console.log('Logo clicked');
            });
        })
        .catch(error => {
            console.error('Error loading interactive logo:', error);
        });
});