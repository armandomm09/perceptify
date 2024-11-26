#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>  // Library required for MQTT

Adafruit_MPU6050 mpu;

float angularVelocityThreshold = 2.7;  // Threshold in rad/s for angular velocity
//float accelerationThreshold = 15.0;    // Threshold in m/s^2 for impact acceleration
//unsigned long stabilityDelay = 1000;   // Stability check delay in milliseconds

bool fallDetected = false;
unsigned long impactTime = 0;

char ssid[] = "LAPTOP 0195";
char pass[] = "123456789";

const char* server = "2.tcp.ngrok.io";
const int mqttPort = 19378;  // Non-secure port
WiFiClient client;
PubSubClient mqttClient(client);

#define channelID "topic"  // Ensure this matches the topic you're publishing to

int status = WL_IDLE_STATUS; 
int connectionDelay = 4;
long lastPublishMillis = 0;
int updateInterval = 0.5;

// Functions to handle WiFi and MQTT connection
void connectWifi();
void mqttConnect();
void mqttSubscribe(const char* subChannelID);
void mqttSubscriptionCallback(char* topic, byte* payload, unsigned int length);
void mqttPublish(const char* pubChannelID, String message);

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("Adafruit MPU6050 test!");

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) delay(10);
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_5_HZ);

  connectWifi();
  mqttClient.setServer(server, mqttPort); 
  mqttClient.setCallback(mqttSubscriptionCallback);
  mqttClient.setBufferSize(2048);
}

void connectWifi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    Serial.print("WiFi Status: ");
    Serial.println(WiFi.status());
    delay(connectionDelay * 1000);
  }

  Serial.println("Connected to Wi-Fi.");
}

void mqttConnect() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    String clientId = "ESP32Client-" + String(WiFi.macAddress());
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWifi();
  }
  if (!mqttClient.connected()) {
    mqttConnect(); 
    mqttSubscribe(channelID);
  }
  
  mqttClient.loop(); 

  if ((millis() - lastPublishMillis) > updateInterval * 1000) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    if (abs(g.gyro.x) > angularVelocityThreshold || abs(g.gyro.y) > angularVelocityThreshold || abs(g.gyro.z) > angularVelocityThreshold) {
      fallDetected = true;
      impactTime = millis();
      Serial.println("High angular velocity detected, possible fall...");
    }
    /*if (fallDetected && (abs(a.acceleration.x) > accelerationThreshold || abs(a.acceleration.y) > accelerationThreshold || abs(a.acceleration.z) > accelerationThreshold)) {
      Serial.println("Impact detected!");
    }*/
    if (fallDetected && (millis() - impactTime > stabilityDelay)) {
      /*if (abs(a.acceleration.x) < 1.0 && abs(a.acceleration.y) < 1.0 && abs(a.acceleration.z) < 1.0) {
        Serial.println("Fall confirmed: Stability detected after impact.");
      }*/
      fallDetected = false;
    }

    // Prepare data to publish
    String message = "{\"gyro_x\":" + String(g.gyro.x, 2) + 
                    ",\"gyro_y\":" + String(g.gyro.y, 2) +
                    ",\"gyro_z\":" + String(g.gyro.z, 2) + 
                    ",\"accel_x\":" + String(a.acceleration.x, 2) +
                    ",\"accel_y\":" + String(a.acceleration.y, 2) +
                    ",\"accel_z\":" + String(a.acceleration.z, 2) + 
                    ",\"fall\":" + String(fallDetected) + 
                    "}";

    mqttPublish(channelID, message);

    //Serial.print("Published acceleration and rotation data: ");
    //Serial.println(message);

    lastPublishMillis = millis();
  }
}

void mqttPublish(const char* pubChannelID, String message) {
  String topicString = String(pubChannelID);
  mqttClient.publish(topicString.c_str(), message.c_str());
}

void mqttSubscribe(const char* subChannelID) {
  String myTopic = String(subChannelID);
  mqttClient.subscribe(myTopic.c_str());
}

void mqttSubscriptionCallback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming messages if necessary
  //Serial.print("Message arrived on topic: ");
  //Serial.println(topic);
  //Serial.print("Message: ");
  //for (unsigned int i = 0; i < length; i++) {
    //Serial.print((char)payload[i]);
  //}
  //Serial.println();
}