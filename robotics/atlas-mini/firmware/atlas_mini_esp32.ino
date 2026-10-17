// Atlas Mini V1: ESP32 Arduino framework. Install ArduinoJson 7 and ESP32 board support.
// Bench prototype ONLY. Servo needs independent regulated 5V supply, common GND.
#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
Servo neck;
constexpr int LED_PIN = 2;
constexpr int SERVO_PIN = 18;
constexpr int MIN_ANGLE = 30;
constexpr int MAX_ANGLE = 150;
constexpr unsigned long LINK_TIMEOUT_MS = 5000;
unsigned long lastCommand = 0;
bool stopped = false;
void reply(const String& id, bool ok, const char* error, JsonVariantConst result) {
  JsonDocument out;
  out["request_id"] = id;
  out["ok"] = ok;
  if (ok) out["result"] = result;
  else out["error"] = error;
  serializeJson(out, Serial); Serial.println();
}
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT); digitalWrite(LED_PIN, LOW);
  neck.setPeriodHertz(50); neck.attach(SERVO_PIN, 500, 2400);
  neck.write(90); lastCommand = millis();
}
void loop() {
  if (millis() - lastCommand > LINK_TIMEOUT_MS) {
    digitalWrite(LED_PIN, LOW);
    // Hold current servo angle; no new motion until valid commands arrive.
  }
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  if (line.length() > 512) return;
  JsonDocument doc;
  if (deserializeJson(doc, line)) return;
  String id = doc["request_id"] | "";
  String cap = doc["capability"] | "";
  String protocol = doc["protocol"] | "";
  JsonDocument result;
  bool ok = true;
  const char* error = "";
  if (protocol != "atlas-hw/1" || id.isEmpty()) { ok=false; error="invalid protocol"; }
  else if (cap == "device.health") {
    result["healthy"] = true; result["protocol"] = "atlas-hw/1"; result["stopped"] = stopped;
  } else if (cap == "robot.estop") {
    stopped = true; digitalWrite(LED_PIN, LOW); result["stopped"] = true;
  } else if (stopped) { ok=false; error="estop latched; physical reset required"; }
  else if (cap == "led.control") {
    if (!doc["arguments"]["on"].is<bool>()) {ok=false; error="invalid LED value";}
    else { bool on = doc["arguments"]["on"].as<bool>(); digitalWrite(LED_PIN, on ? HIGH : LOW); result["on"] = on; }
  } else if (cap == "servo.set_angle") {
    JsonVariant angle = doc["arguments"]["angle"];
    if (!angle.is<int>() || angle.as<int>() < MIN_ANGLE || angle.as<int>() > MAX_ANGLE) {ok=false; error="invalid angle";}
    else {neck.write(angle.as<int>()); result["angle"] = angle.as<int>();}
  } else {ok=false; error="unsupported capability";}
  if (ok) lastCommand = millis();
  reply(id, ok, error, result.as<JsonVariantConst>());
}
