#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Servo.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// ---------------- PINS ----------------
#define SERVO_PIN 27
#define SENSOR_PIN 14
#define ONE_WIRE_BUS 13
#define BUZZER_PIN 32

// ---------------- WIFI ----------------
const char* ssid = "WiFi-UMBK";
const char* password = "UMBK2023";
const char* serverUrl = "http://192.168.35.5:5000/api/count";

// ---------------- OBJECTS ----------------
Servo gasServo;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// ---------------- FLAGS ----------------
bool whistleLatched = false;
bool servoClosed = false;
bool sentAlert = false;


void setup() {
  Serial.begin(115200);

  pinMode(SENSOR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(BUZZER_PIN, LOW);
  gasServo.attach(SERVO_PIN);
  ;
  delay(1000);

  // Servo
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  gasServo.setPeriodHertz(50);
  gasServo.attach(SERVO_PIN, 500, 2400);

  
  delay(1000);

  Serial.println("Servo initialized");

  sensors.begin();

  // WiFi
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected");
  Serial.println(WiFi.localIP());
}

void loop() {

  // ---------- TEMPERATURE ----------
  sensors.requestTemperatures();
  float temp = sensors.getTempCByIndex(0);
  float currentTemp = sensors.getTempCByIndex(0);
  Serial.println("Current Temperature: " + String(currentTemp) + " °C");

  if (temp != DEVICE_DISCONNECTED_C) {

    if (temp >= 122.0) {

      HTTPClient http;
      http.begin("http://192.168.3.5:5000/temperature_alert");

      int code = http.GET();

      Serial.print("Response: ");
      Serial.println(code);

      http.end();

      sentAlert = true;

    if (temp < 28.0 && sentAlert) {
      http.begin("http://192.168.3.5:5000/clear_alert");
      http.GET();
      sentAlert = false;
     }

      Serial.println("Temperature exceeded!");

      digitalWrite(BUZZER_PIN, HIGH);

      if (!servoClosed) {
        gasServo.write(180);
        servoClosed = true;
      }

      delay(500);
      return;
    }

    digitalWrite(BUZZER_PIN, LOW);
  }

  // ---------- WHISTLE DETECTION ----------
  int sensorState = digitalRead(SENSOR_PIN);

  if (sensorState == HIGH && !whistleLatched) {

    whistleLatched = true;

    Serial.println("Whistle detected");

    sendWhistleCount();
  }

  if (sensorState == LOW && whistleLatched) {

    delay(100);

    if (digitalRead(SENSOR_PIN) == LOW) {

      whistleLatched = false;

      Serial.println("Ready for next whistle");
    }
  }

  delay(50);
}

void sendWhistleCount() {

  if (WiFi.status() != WL_CONNECTED)
    return;

  HTTPClient http;

  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST("{}");

  if (httpCode > 0) {

    String payload = http.getString();

    Serial.println("Flask Response:");
    Serial.println(payload);

    DynamicJsonDocument doc(256);

    DeserializationError error =
        deserializeJson(doc, payload);

    if (error) {

      Serial.print("JSON Error: ");
      Serial.println(error.c_str());

      http.end();
      return;
    }

    int remaining = doc["remaining"];

    Serial.print("Remaining = ");
    Serial.println(remaining);

   if (remaining == 0) {
    Serial.println("MOVING SERVO");


    

    gasServo.attach(SERVO_PIN);
    delay(100);

    // Force full movement
    gasServo.write(180);

    delay(3000);

    servoClosed = true;
    servoClosed = true;

   }
  else {

    Serial.print("HTTP Error: ");
    Serial.println(http.errorToString(httpCode));
  }

  http.end();
}}