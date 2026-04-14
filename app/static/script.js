const STADIUMS = {
    "eden_gardens": {
        "id": "eden_gardens",
        "name": "Eden Gardens",
        "lat": 22.564551128342874,
        "lng": 88.34331627118985
    },
    "wankhede": {
        "id": "wankhede",
        "name": "Wankhede Stadium",
        "lat": 18.938888,
        "lng": 72.825833
    },
    "narendra_modi": {
        "id": "narendra_modi",
        "name": "Narendra Modi Stadium",
        "lat": 23.091763,
        "lng": 72.597519
    }
};

let currentStadiumId = "eden_gardens";
let map;
let heatmap;
let crowdDataInterval;

// DOM Elements
const chatArea = document.getElementById('chat-area');
const chatInput = document.getElementById('chat-input');
const guideMeBtn = document.getElementById('guide-me-btn');
const mapPlaceholder = document.getElementById('map-placeholder');
const stadiumNameLabel = document.getElementById('stadium-name');

function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    return R * c; 
}

function detectNearestStadium() {
    return new Promise((resolve) => {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const userLat = position.coords.latitude;
                    const userLng = position.coords.longitude;
                    
                    let nearest = "eden_gardens";
                    let minDistance = Infinity;

                    for (const key in STADIUMS) {
                        const dist = getDistance(userLat, userLng, STADIUMS[key].lat, STADIUMS[key].lng);
                        if (dist < minDistance) {
                            minDistance = dist;
                            nearest = key;
                        }
                    }
                    resolve(nearest);
                },
                (error) => {
                    console.error("Geolocation error:", error);
                    resolve("eden_gardens"); // Fallback
                },
                { timeout: 5000 }
            );
        } else {
            resolve("eden_gardens");
        }
    });
}

function appendMessage(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    // Convert newlines to breaks or markdown logic simple
    const formattedText = text.replace(/\n/g, '<br>');
    
    msgDiv.innerHTML = `
        <div class="avatar">${isUser ? '👤' : '🤖'}</div>
        <div class="bubble">${formattedText}</div>
    `;
    chatArea.appendChild(msgDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage(text, true);
    chatInput.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, stadium_id: currentStadiumId })
        });
        const data = await response.json();
        
        appendMessage(data.message, false);

        if (data.coordinates && map) {
            map.panTo({ lat: data.coordinates.lat, lng: data.coordinates.lng });
            map.setZoom(18); // Zoom in closer on recommendation
            
            // Add a temporary marker
            new google.maps.Marker({
                position: { lat: data.coordinates.lat, lng: data.coordinates.lng },
                map: map,
                animation: google.maps.Animation.DROP,
                icon: 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png'
            });
        }
    } catch (err) {
        console.error("Chat error:", err);
        appendMessage("Sorry, I'm having trouble connecting to the backend.", false);
    }
}

async function loadCrowdData() {
    try {
        const res = await fetch(`/api/stadium/${currentStadiumId}/crowd-data`);
        const result = await res.json();
        const data = result.data;
        
        if (map && window.google && google.maps.visualization) {
            // Update heatmap
            const heatmapPoints = data.heatmap.map(pt => {
                return {
                    location: new google.maps.LatLng(pt.lat, pt.lng),
                    weight: pt.weight
                };
            });
            
            if (heatmap) {
                heatmap.setData(heatmapPoints);
            } else {
                heatmap = new google.maps.visualization.HeatmapLayer({
                    data: heatmapPoints,
                    map: map,
                    radius: 25,
                    opacity: 0.7,
                    gradient: [
                        'rgba(0, 255, 0, 0)',
                        'rgba(0, 255, 0, 1)',
                        'rgba(255, 255, 0, 1)',
                        'rgba(255, 0, 0, 1)'
                    ]
                });
            }
        }
    } catch(err) {
        console.error("Error loading crowd data:", err);
    }
}

function initMap() {
    const defaultLocation = { lat: STADIUMS[currentStadiumId].lat, lng: STADIUMS[currentStadiumId].lng };
    
    // Dark map styling array
    const darkMapStyle = [
      { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
      { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
      { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
      {
        featureType: "administrative.locality",
        elementType: "labels.text.fill",
        stylers: [{ color: "#d59563" }],
      },
      {
        featureType: "poi",
        elementType: "labels.text.fill",
        stylers: [{ color: "#d59563" }],
      },
      {
        featureType: "road",
        elementType: "geometry",
        stylers: [{ color: "#38414e" }],
      },
      {
        featureType: "road",
        elementType: "geometry.stroke",
        stylers: [{ color: "#212a37" }],
      },
      {
        featureType: "water",
        elementType: "geometry",
        stylers: [{ color: "#17263c" }],
      }
    ];

    mapPlaceholder.style.display = 'none';

    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 16,
        center: defaultLocation,
        styles: darkMapStyle,
        disableDefaultUI: true, // cleaner look
        zoomControl: true
    });

    // Start crowd data polling
    loadCrowdData();
    if (crowdDataInterval) clearInterval(crowdDataInterval);
    crowdDataInterval = setInterval(loadCrowdData, 10000);
}

// Map initiation fallback
window.initMap = initMap;

async function bootApp() {
    // 1. Detect Stadium
    stadiumNameLabel.textContent = "Detecting location...";
    currentStadiumId = await detectNearestStadium();
    const stadium = STADIUMS[currentStadiumId];
    stadiumNameLabel.textContent = `Active Venue: ${stadium.name}`;

    // 2. Load API keys configuration
    const configRes = await fetch('/api/config');
    const config = await configRes.json();
    
    // 3. Load Map Script
    if (config.google_maps_api_key) {
        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${config.google_maps_api_key}&libraries=visualization&callback=initMap`;
        script.async = true;
        document.head.appendChild(script);
    } else {
        // Fallback UI
        mapPlaceholder.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <p>⚠️ Google Maps API Key not found.</p>
                <p>Map view is disabled, but chat fallback is working. Please add your key to the .env file.</p>
                <p style="margin-top: 10px; color: var(--primary-magenta);">Selected Venue: ${stadium.name}</p>
            </div>
        `;
    }

    // 4. Setup Chat listeners
    guideMeBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

// Start
document.addEventListener("DOMContentLoaded", bootApp);
