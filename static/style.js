const API_KEY = 'smartchili-api-key-2025';
const API_BASE_URL = '/api/v1';
const HUMIDITY_POLLING_INTERVAL_MS = 3000;
let humidityPollingTimer = null;
let classificationPollingTimer = null;
let classificationPollingHour = 16;
let classificationPollingMinute = 25;

async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE_URL}/config`, {
            headers: {
                'X-API-Key': API_KEY
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.classification_polling_hours !== undefined) {
                classificationPollingHour = data.classification_polling_hours;
            }
            if (data.classification_polling_minutes !== undefined) {
                classificationPollingMinute = data.classification_polling_minutes;
            }
            console.log(`Jadwal polling klasifikasi: ${classificationPollingHour}:${classificationPollingMinute.toString().padStart(2, '0')}`);
        }
    } catch (error) {
        console.error('Error saat memuat konfigurasi:', error);
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
    const targetTime = `${classificationPollingHour}:${classificationPollingMinute.toString().padStart(2, '0')}`;
    
    if (currentHour === classificationPollingHour && currentMinute === classificationPollingMinute) {
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
        const response = await fetch(`${API_BASE_URL}/kelembapan`, {
            headers: {
                'X-API-Key': API_KEY
            }
        });
        
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

async function uploadImage() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Silakan pilih file gambar terlebih dahulu');
        return;
    }
    
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showError('Format file tidak valid. Gunakan JPG, PNG, atau WEBP');
        return;
    }
    
    if (file.size > 10485760) {
        showError('Ukuran file terlalu besar. Maksimal 10MB');
        return;
    }
    
    hideError();
    showLoading();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload-gambar`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Gagal mengunggah gambar');
        }
        
        hideLoading();
        updateDisplay(data);
        
    } catch (error) {
        hideLoading();
        showError(`Error: ${error.message}`);
        console.error('Error saat upload:', error);
    }
}

function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('uploadBtn').disabled = true;
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('uploadBtn').disabled = false;
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideError() {
    document.getElementById('error').style.display = 'none';
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
        const response = await fetch(`${API_BASE_URL}/hasil-klasifikasi?limit=1`, {
            headers: {
                'X-API-Key': API_KEY
            }
        });
        
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
    loadConfig().then(() => {
        loadLatestClassification();
        startHumidityPolling();
        startClassificationScheduler();
    });
    
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', function() {
        hideError();
    });
});

window.addEventListener('beforeunload', function() {
    stopHumidityPolling();
    stopClassificationScheduler();
});
