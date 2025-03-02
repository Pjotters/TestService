// Verander dit naar jouw backend URL
const API_URL = 'https://securis-m7bb.onrender.com';

let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let status = document.getElementById('status');
let loginBtn = document.getElementById('loginBtn');

// Start camera
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        status.textContent = 'Camera toegang mislukt';
        console.error(err);
    }
}

// Login functie
async function loginWithIris() {
    try {
        status.textContent = 'Scanning...';
        
        // Neem foto
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        // Stuur naar backend
        const imageData = canvas.toDataURL('image/jpeg');
        const response = await fetch(`${API_URL}/api/login-with-iris`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        });

        const data = await response.json();
        if (data.success) {
            // Sla token op
            localStorage.setItem('auth_token', data.token);
            status.textContent = 'Login succesvol! Doorsturen...';
            // Redirect naar dashboard (pas aan naar jouw URL)
            window.location.href = '/dashboard.html';
        } else {
            status.textContent = data.message;
        }
    } catch (err) {
        status.textContent = 'Login mislukt';
        console.error(err);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', startCamera);
loginBtn.addEventListener('click', loginWithIris);
