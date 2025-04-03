document.addEventListener('DOMContentLoaded', function() {
    // Initialize map if the map element exists
    const mapElement = document.getElementById('map');
    if (mapElement) {
        initMap();
    }
});

function initMap() {
    // Clinic location coordinates for Budigere Road, Bengaluru
    const clinicLocation = [13.0617, 77.7213]; // Budigere Road, Bengaluru coordinates
    
    // Initialize map
    const map = L.map('map').setView(clinicLocation, 15);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Add marker for clinic location
    const clinicMarker = L.marker(clinicLocation).addTo(map);
    
    // Add popup to marker
    clinicMarker.bindPopup("<strong>Dr. Richa's Eye Clinic</strong><br>Your Vision, Our Priority").openPopup();
    
    // Add circle around the marker
    L.circle(clinicLocation, {
        color: '#007bff',
        fillColor: '#007bff',
        fillOpacity: 0.1,
        radius: 500
    }).addTo(map);
}

// Function to open Google Maps with directions from user's location to clinic
function getDirectionsToClinic() {
    // Clinic location coordinates for Budigere Road, Bengaluru
    const clinicLat = 13.0617;
    const clinicLng = 77.7213;
    
    // Clinic address
    const clinicAddress = encodeURIComponent("Dr. Richa's Eye Clinic, First floor, DVR Town Centre, near to IGUS private limited, Mandur, Budigere Road, Bengaluru, Karnataka 560049, India");
    
    // Try to get user's current location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            // Success callback
            function(position) {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;
                
                // Open Google Maps with directions from user's location to clinic
                const mapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${clinicAddress}`;
                window.open(mapsUrl, '_blank');
            },
            // Error callback
            function() {
                // If cannot get user's location, just show directions to clinic
                const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${clinicAddress}`;
                window.open(mapsUrl, '_blank');
            }
        );
    } else {
        // Geolocation not supported
        const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${clinicAddress}`;
        window.open(mapsUrl, '_blank');
    }
}
