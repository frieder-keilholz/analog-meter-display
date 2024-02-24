// ESP32 code for the WiFi meter
// using PWM to control the current output
// !set to work with an 5mA amperemeter!

#define PIN  27 // YOUR PWM GPIO PIN

#include <WiFi.h>

// Daten des WiFi-Netzwerks
const char* ssid     = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

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

// old
long randNumber;
int targetMA;

void setup() {
  Serial.begin(115200);

  gpio_set_drive_capability((gpio_num_t)PIN, GPIO_DRIVE_CAP_0); // Set drive strength to ~10mA
  ledcSetup(ledChannel, freq, resolution);
  ledcAttachPin(PIN, ledChannel);
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
        //Serial.write(c);                    // print it out the serial monitor
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
            
            // turns the GPIOs on and off
            if (header.indexOf("GET /util/") >= 0) {
              Serial.println("UTIL set");
              String value = header.substring(header.indexOf("GET /util/")+10);
              value = value.substring(0,value.indexOf('/'));
              Serial.println(value);
              int util = value.toInt();
              int duty = util * 1.15;
              if(duty > limitDuty) duty = limitDuty;
              ledcWrite(ledChannel, duty);
            }
            client.println();
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