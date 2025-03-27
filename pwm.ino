#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

#define sub "A" 
#define pub "A_tt"
#define sub1 "T" 
#define pub1 "T_tt"

#define button_d 3 
#define button_q 32 
#define RL 1 
#define RL1 14 

const char* ssid = "aaaaaa";  
const char* password = "223332323"; 

const char* mqtt_server = "9ba9df.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_username = "....tanhc"; 
const char* mqtt_password = "........"; 

WiFiClientSecure espClient;
PubSubClient client(espClient);

int RL_tt = 0; 
int pwm_muc[] = {0, 64, 168, 255};
int current_muc = 0;
bool lastButtonState = HIGH;

void setup_wifi(){
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { 
    Serial.print(".");
    delay(500);
  }
  Serial.println("WiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32-" + String(random(1000, 9999)); 
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("MQTT connected");
      client.subscribe(sub);
      client.subscribe(sub1);
    } else {
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) { 
  if ((char)payload[0] == '1') {
    client.publish(pub, "Den Bat");
    digitalWrite(RL, HIGH);
    RL_tt = 1;
  } else {
    client.publish(pub, "Den Tat");
    digitalWrite(RL, LOW);
    RL_tt = 0;
  }
}

void callback1(char* topic, byte* payload, unsigned int length) { 
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  int pwm_value = message.toInt(); 
  pwm_value = constrain(pwm_value, 0, 255); 
  int new_muc = 0;
  for (int i = 0; i < 4; i++) {
    if (pwm_value == pwm_muc[i]) {
      new_muc = i;
      break;
    }
  }
  current_muc = new_muc;
}

void DK_nutan() {
  if (digitalRead(button_d) == LOW) {
    delay(200);
    RL_tt = !RL_tt;
    digitalWrite(RL, RL_tt);
    client.publish(pub, RL_tt ? "Den Bat" : "Den Tat");
  }
}

void handleButton() {
  bool buttonState = digitalRead(button_q);
  if (buttonState == LOW && lastButtonState == HIGH) {
    delay(200);
    current_muc = (current_muc + 1) % 4;
    String response = "Muc_" + String(current_muc);
    client.publish(pub1, response.c_str());
  }
  lastButtonState = buttonState;
}

void generatePWM(int pin, int dutyCycle, int frequency) {
  int period = 1000000 / frequency; //chu kì (micro giay (ms)) của xung pwm 1s = 1.000.000 / tần số
  int highTime = (period * dutyCycle) / 255; // thời gian bật =  chu kỳ xung cao 
  int lowTime = period - highTime;
  digitalWrite(pin, HIGH);
  delayMicroseconds(highTime);
  digitalWrite(pin, LOW);
  delayMicroseconds(lowTime);
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  espClient.setInsecure();  
  client.setCallback(callback);
  client.setCallback(callback1);

  pinMode(button_d, INPUT_PULLUP);
  pinMode(button_q, INPUT_PULLUP);  
  pinMode(RL, OUTPUT);
  pinMode(RL1, OUTPUT);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  DK_nutan();
  handleButton();
  generatePWM(RL1, pwm_muc[current_muc], 5000);
  client.loop();
}
