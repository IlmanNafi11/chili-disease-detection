#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

#define SENSOR_PIN 35
#define RELAY_PIN 26

const char* WIFI_SSID     = "POCO M3";
const char* WIFI_PASSWORD = "11111111";

const char* API_BASE_URL  = "https://agrochilisense.builtwithafi.web.id/api/v1";
const char* API_ENDPOINT  = "/data-kelembapan";
const char* API_KEY       = "your-api-key-here";

const unsigned long INTERVAL_KIRIM_MS = 5000;
unsigned long lastKirimMillis = 0;

const int NILAI_BASAH  = 1234;
const int NILAI_KERING = 4095;
const int BATAS_KELEMBAPAN = 60;
const unsigned long DEBOUNCE_MS = 5000;

bool pompaNyala = false;
bool targetPompaNyala = false;
unsigned long waktuPerubahanKondisiTerakhir = 0;

int hitungKelembapanPersen(int adcValue) {
  if (adcValue <= NILAI_BASAH)  return 100;
  if (adcValue >= NILAI_KERING) return 0;

  long rentang = (long)NILAI_KERING - (long)NILAI_BASAH;
  long selisihDariKering = (long)NILAI_KERING - adcValue;

  int persen = (int)(selisihDariKering * 100 / rentang);
  if (persen < 0)   persen = 0;
  if (persen > 100) persen = 100;

  return persen;
}

void kirimDataKelembapan(int kelembapan) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTPS] WiFi tidak terhubung, batal kirim data.");
    return;
  }

  WiFiClientSecure client;
  HTTPClient http;

  client.setInsecure();

  String url = String(API_BASE_URL) + String(API_ENDPOINT);
  if (!http.begin(client, url)) {
    Serial.println("[HTTPS] Gagal inisialisasi koneksi.");
    return;
  }

  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", API_KEY);

  String body = String("{\"kelembapan\": ") + String(kelembapan) + String("}");

  Serial.print("[HTTPS] POST ");
  Serial.print(url);
  Serial.print(" body: ");
  Serial.println(body);

  int httpCode = http.POST(body);

  if (httpCode > 0) {
    Serial.print("[HTTPS] Response code: ");
    Serial.println(httpCode);
    String payload = http.getString();
    Serial.print("[HTTPS] Response body: ");
    Serial.println(payload);
  } else {
    Serial.print("[HTTPS] POST gagal, error: ");
    Serial.println(http.errorToString(httpCode));
  }

  http.end();
}

void setup() {
  Serial.begin(115200);
  pinMode(SENSOR_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, HIGH);
  pompaNyala = false;
  targetPompaNyala = false;
  waktuPerubahanKondisiTerakhir = millis();
  lastKirimMillis = millis();

  Serial.println();
  Serial.print("Menghubungkan ke WiFi: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int maxRetry = 30;
  while (WiFi.status() != WL_CONNECTED && maxRetry > 0) {
    delay(500);
    Serial.print(".");
    maxRetry--;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi tersambung, IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Gagal terhubung WiFi, lanjut tanpa koneksi.");
  }
}

void loop() {
  int sensorValue = analogRead(SENSOR_PIN);
  int kelembapan = hitungKelembapanPersen(sensorValue);
  unsigned long sekarang = millis();

  bool targetBaru = (kelembapan <= BATAS_KELEMBAPAN);

  if (targetBaru != targetPompaNyala) {
    targetPompaNyala = targetBaru;
    waktuPerubahanKondisiTerakhir = sekarang;
  }

  bool bolehUbahStatus =
      (sekarang - waktuPerubahanKondisiTerakhir >= DEBOUNCE_MS);

  if (bolehUbahStatus && (pompaNyala != targetPompaNyala)) {
    pompaNyala = targetPompaNyala;
    digitalWrite(RELAY_PIN, pompaNyala ? LOW : HIGH);
  }

  Serial.print("ADC: ");
  Serial.print(sensorValue);
  Serial.print(" | Kelembapan: ");
  Serial.print(kelembapan);
  Serial.print("%");

  Serial.print(" | TargetPompa: ");
  Serial.print(targetPompaNyala ? "ON" : "OFF");

  Serial.print(" | PompaAktual: ");
  Serial.print(pompaNyala ? "ON" : "OFF");
  Serial.print(" | ");

  if (!bolehUbahStatus && (pompaNyala != targetPompaNyala)) {
    unsigned long sisa =
        (DEBOUNCE_MS - (sekarang - waktuPerubahanKondisiTerakhir)) / 1000;
    Serial.print("Menunggu stabil ~");
    Serial.print(sisa + 1);
    Serial.println(" dtk...");
  } else {
    Serial.println(pompaNyala ? "MENYIRAM..." : "MATI...");
  }

  if (sekarang - lastKirimMillis >= INTERVAL_KIRIM_MS) {
    lastKirimMillis = sekarang;
    kirimDataKelembapan(kelembapan);
  }

  delay(500);
}