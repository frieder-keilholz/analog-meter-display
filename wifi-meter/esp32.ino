#define AMPEREMETER_PIN_0  27 //
#define AMPEREMETER_PIN_1  14
#define LED_PIN 17
#define NUMPIXELS 4

#include <WiFi.h>
#include <Adafruit_NeoPixel.h>

// Daten des WiFi-Netzwerks
const char* ssid     = "Nein";
const char* password = "Nein";

// Port des Webservers auf 80 setzen
WiFiServer server(80);
long currentTime = millis();
long previousTime = 0;
int timeoutTime = 3000;
String header;

// setting PWM properties
const int freq = 5000;
const int ledChannel = 0;
const int resolution = 8;
// set amperemeter limit duty
int limitDuty = 120;

// WS2812B LED
Adafruit_NeoPixel ws2812b = Adafruit_NeoPixel(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

void processData(String data) {
  //Serial.println(data);
  while (data.length() >= 18 && data.startsWith("/A"))  // Check if the string starts with '/A' and has enough length
  {
    String amperemeterData = data.substring(0, 18);
    Serial.println(amperemeterData);
    int amperemeterTarget = amperemeterData.substring(2, 3).toInt();
    int util = amperemeterData.substring(5, 7).toInt();
    int red = amperemeterData.substring(9, 12).toInt();
    int green = amperemeterData.substring(12, 15).toInt();
    int blue = amperemeterData.substring(15, 18).toInt();
    Serial.println("Target: " + String(amperemeterTarget) + ", Util: " + String(util) + ", Red: " + String(red) + ", Green: " + String(green) + ", Blue: " + String(blue));
    data = data.substring(18);
  }
  
}

void setup() {
  Serial.begin(115200);

  ws2812b.begin();

  gpio_set_drive_capability((gpio_num_t)AMPEREMETER_PIN_0, GPIO_DRIVE_CAP_0); // Set drive strength to ~10mA
  gpio_set_drive_capability((gpio_num_t)AMPEREMETER_PIN_1, GPIO_DRIVE_CAP_0); // Set drive strength to ~10mA
  ledcSetup(ledChannel, freq, resolution);
  ledcSetup(ledChannel+1, freq, resolution);
  ledcAttachPin(AMPEREMETER_PIN_0, ledChannel);
  ledcAttachPin(AMPEREMETER_PIN_1, ledChannel+1);
  /*
  randomSeed(analogRead(0));
  */
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  // Print local IP address and start web server
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();
  delay(1000);
  Serial.println("Server up");
}

void loop(){
  WiFiClient client = server.available();   // Listen for incoming clients

  if (client) {                             // If a new client connects,
    currentTime = millis();
    previousTime = currentTime;
    Serial.println("New Client.");          // print a message out in the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    while (client.connected() && currentTime - previousTime <= timeoutTime) {  // loop while the client's connected
      currentTime = millis();
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out the serial monitor
        header += c;
        if (c == '\n') {                    // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            if (header.indexOf("GET /A") >= 0) {
              String data = header.substring(4);
              processData(data); // Methode aufrufen und String ausgeben
            }
            else{
              Serial.write("[ERR] not a get request");
            }
            
            break;
          }else{
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    header = "";
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
  }

}