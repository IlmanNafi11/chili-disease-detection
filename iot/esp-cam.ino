#include "esp_camera.h"
#include <WiFi.h>

const char* ssid = "Redmi 13";
const char* password = "ilmannafi";
const char* serverIP = "172.16.108.109";
const int serverPort = 8000;
const char* serverPath = "/api/v1/upload-gambar";
const char* apiKey = "smartchili-api-key-2025";

// Konfigurasi kamera AI Thinker ESP32-CAM
camera_config_t config = {
  .pin_pwdn       = 32,
  .pin_reset      = -1,
  .pin_xclk       = 0,
  .pin_sccb_sda   = 26,
  .pin_sccb_scl   = 27,
  .pin_d7         = 35,
  .pin_d6         = 34,
  .pin_d5         = 39,
  .pin_d4         = 36,
  .pin_d3         = 21,
  .pin_d2         = 19,
  .pin_d1         = 18,
  .pin_d0         = 5,
  .pin_vsync      = 25,
  .pin_href       = 23,
  .pin_pclk       = 22,
  .xclk_freq_hz   = 20000000,
  .ledc_timer     = LEDC_TIMER_0,
  .ledc_channel   = LEDC_CHANNEL_0,
  .pixel_format   = PIXFORMAT_JPEG,
  .frame_size     = FRAMESIZE_VGA,
  .jpeg_quality   = 12,
  .fb_count       = 1
};

void startCamera() {
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed 0x%x\n", err);
    while (true) delay(1000);
  }
  Serial.println("Camera OK");
}

bool uploadImage(camera_fb_t * fb) {
  WiFiClient client;
  if (!client.connect(serverIP, serverPort)) {
    Serial.println("Gagal konek ke server!");
    return false;
  }

  String boundary = "----ESP32CAMBoundary";
  String head = "--" + boundary + "\r\n"
                "Content-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\n"
                "Content-Type: image/jpeg\r\n\r\n";
  String tail = "\r\n--" + boundary + "--\r\n";

  size_t contentLength = head.length() + fb->len + tail.length();

  // 🔹 Header HTTP ditambahkan dengan X-API-Key
  client.printf("POST %s HTTP/1.1\r\n", serverPath);
  client.printf("Host: %s\r\n", serverIP);
  client.printf("X-API-Key: %s\r\n", apiKey);
  client.println("Content-Type: multipart/form-data; boundary=" + boundary);
  client.printf("Content-Length: %d\r\n", contentLength);
  client.println("Connection: close\r\n");

  client.print(head);
  client.write(fb->buf, fb->len);
  client.print(tail);

  // Print respon server
  while (client.connected()) {
    if (client.available()) Serial.write(client.read());
  }
  client.stop();
  return true;
}

void setup() {
  Serial.begin(115200);
  Serial.println("\nBooting...");

  WiFi.begin(ssid, password);
  Serial.print("Menghubungkan ke WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Terhubung! IP ESP32: ");
  Serial.println(WiFi.localIP());

  startCamera();
  delay(2000);
}

void loop() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Gagal capture");
    delay(1000);
    return;
  }

  Serial.printf("Captured %u bytes\n", fb->len);
  if (uploadImage(fb)) Serial.println("Upload OK");
  else Serial.println("Upload Gagal");

  esp_camera_fb_return(fb);
  delay(10000); // ambil tiap 10 detik
}
