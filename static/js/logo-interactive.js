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
            
            // Get reference to all required SVG elements
            const eye = svgElement.getElementById('eye');
            const pupil = svgElement.getElementById('pupil');
            const reflectionDot = svgElement.getElementById('reflectionDot');
            const topEyelid = svgElement.getElementById('topEyelid');
            const bottomEyelid = svgElement.getElementById('bottomEyelid');
            
            if (!eye || !pupil || !reflectionDot || !topEyelid || !bottomEyelid) {
                console.error('SVG elements not found');
                return;
            }
            
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
            
            // Handle mouse movement for pupil tracking
            document.addEventListener('mousemove', function(evt) {
                // Calculate mouse position relative to the SVG
                const rect = svgElement.getBoundingClientRect();
                const mouseX = evt.clientX - rect.left;
                const mouseY = evt.clientY - rect.top;
                
                // Move pupil slightly to follow mouse (limit movement)
                const eyeCenterX = 25; // Updated eye center position
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
                reflectionDot.setAttribute('cx', 27 - dx/2);
                reflectionDot.setAttribute('cy', 27 - dy/2);
            });
            
            // Blink when mouse enters the eye
            eye.addEventListener('mouseenter', function() {
                blinkEye();
            });
            
            // Continuous blinking every 4 seconds
            setInterval(blinkEye, 4000);
            
            // Add click handler
            svgElement.addEventListener('click', function() {
                // Trigger a blink
                blinkEye();
                
                // If the logo should link to the homepage or admin login
                // We already have this handled in layout.html
            });
        })
        .catch(error => {
            console.error('Error loading interactive logo:', error);
        });
});