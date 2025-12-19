// Configuration will be loaded from window.APP_CONFIG (injected by backend)
let API_KEY = '';
let API_BASE_URL = '/api/v1';
let HUMIDITY_POLLING_INTERVAL_MS = 3000;
let CLASSIFICATION_POLLING_HOUR = 15;
let CLASSIFICATION_POLLING_MINUTE = 28;
let humidityPollingTimer = null;
let classificationPollingTimer = null;

// Load configuration from window object
function loadConfiguration() {
    if (window.APP_CONFIG) {
        API_KEY = window.APP_CONFIG.API_KEY || '';
        API_BASE_URL = window.APP_CONFIG.API_BASE_URL || '/api/v1';
        HUMIDITY_POLLING_INTERVAL_MS = window.APP_CONFIG.HUMIDITY_POLLING_INTERVAL_MS || 3000;
        CLASSIFICATION_POLLING_HOUR = window.APP_CONFIG.CLASSIFICATION_POLLING_HOUR || 15;
        CLASSIFICATION_POLLING_MINUTE = window.APP_CONFIG.CLASSIFICATION_POLLING_MINUTE || 28;
    } else {
        console.warn('⚠️ APP_CONFIG not found, using defaults');
    }
}

function startClassificationScheduler() {
    checkAndLoadClassification();
    
    if (classificationPollingTimer) {
        clearInterval(classificationPollingTimer);
    }
    
    classificationPollingTimer = setInterval(() => {
        checkAndLoadClassification();
    }, 10000);
}

let lastCheckedMinute = -1;

function checkAndLoadClassification() {
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentSecond = now.getSeconds();
    
    const timeString = `${currentHour}:${currentMinute.toString().padStart(2, '0')}:${currentSecond.toString().padStart(2, '0')}`;
    const targetTime = `${CLASSIFICATION_POLLING_HOUR}:${CLASSIFICATION_POLLING_MINUTE.toString().padStart(2, '0')}`;
    
    if (currentHour === CLASSIFICATION_POLLING_HOUR && currentMinute === CLASSIFICATION_POLLING_MINUTE) {
        if (lastCheckedMinute !== currentMinute) {
            console.log(`⏰ Waktu polling tercapai! Loading klasifikasi... (${timeString})`);
            loadLatestClassification();
            lastCheckedMinute = currentMinute;
        }
    } else {
        if (currentSecond === 0) {
            console.log(`⏱️ Check waktu: ${timeString} | Target: ${targetTime}`);
        }
    }
}

function stopClassificationScheduler() {
    if (classificationPollingTimer) {
        clearInterval(classificationPollingTimer);
        classificationPollingTimer = null;
    }
}

function startHumidityPolling() {
    loadHumidity();
    
    if (humidityPollingTimer) {
        clearInterval(humidityPollingTimer);
    }
    
    humidityPollingTimer = setInterval(() => {
        loadHumidity();
    }, HUMIDITY_POLLING_INTERVAL_MS);
}

function stopHumidityPolling() {
    if (humidityPollingTimer) {
        clearInterval(humidityPollingTimer);
        humidityPollingTimer = null;
        console.log('Humidity polling stopped');
    }
}

async function loadHumidity() {
    try {
        const response = await fetch(`${API_BASE_URL}/kelembapan`);
        
        const data = await response.json();
        
        const kelembapanElement = document.getElementById('kelembapan');
        if (response.ok && data.success && data.kelembapan !== -1.0 && data.kelembapan !== null && data.kelembapan !== undefined) {
            kelembapanElement.textContent = `${data.kelembapan.toFixed(1)}%`;
            kelembapanElement.className = '';
        } else {
            kelembapanElement.textContent = 'Tidak Tersedia';
            kelembapanElement.className = '';
        }
    } catch (error) {
        console.error('Error saat memuat data kelembapan:', error);
        const kelembapanElement = document.getElementById('kelembapan');
        kelembapanElement.textContent = 'Tidak Tersedia';
        kelembapanElement.className = '';
    }
}





function updateDisplay(data) {
    const displayImage = document.getElementById('displayImage');
    if (data.gambar_url) {
        displayImage.src = data.gambar_url + '?t=' + new Date().getTime();
        displayImage.alt = 'Hasil Klasifikasi';
    }
    
    const statusElement = document.getElementById('status');
    if (data.hasil !== undefined && data.hasil !== null) {
        statusElement.textContent = data.hasil === 0 ? 'Sehat' : 'Sakit';
        statusElement.className = data.hasil === 0 ? 'status-sehat' : 'status-sakit';
    } else {
        statusElement.textContent = 'Tidak Tersedia';
        statusElement.className = '';
    }
    
    const waktuElement = document.getElementById('waktu');
    if (data.upload_time) {
        const uploadTime = new Date(data.upload_time);
        waktuElement.textContent = uploadTime.toLocaleString('id-ID');
    } else if (data.timestamp) {
        const timestamp = new Date(data.timestamp);
        waktuElement.textContent = timestamp.toLocaleString('id-ID');
    } else {
        waktuElement.textContent = 'N/A';
    }
    
    loadHumidity();
}

async function loadLatestClassification() {
    try {
        const response = await fetch(`${API_BASE_URL}/hasil-klasifikasi?limit=1`);
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.results && data.results.length > 0) {
                updateDisplay(data.results[0]);
            } else {
                setDefaultDisplay();
            }
        } else {
            setDefaultDisplay();
        }
    } catch (error) {
        console.error('Error saat memuat data klasifikasi terbaru:', error);
        setDefaultDisplay();
    }
}

function setDefaultDisplay() {
    const displayImage = document.getElementById('displayImage');
    displayImage.src = '/static/PlaceholderImage.png';
    displayImage.alt = 'Placeholder';
    
    const statusElement = document.getElementById('status');
    statusElement.textContent = 'Tidak Tersedia';
    statusElement.className = '';
    
    const waktuElement = document.getElementById('waktu');
    waktuElement.textContent = 'N/A';
    
    loadHumidity();
}

document.addEventListener('DOMContentLoaded', function() {
    loadConfiguration();
    loadLatestClassification();
    startHumidityPolling();
    startClassificationScheduler();
});

window.addEventListener('beforeunload', function() {
    stopHumidityPolling();
    stopClassificationScheduler();
});
