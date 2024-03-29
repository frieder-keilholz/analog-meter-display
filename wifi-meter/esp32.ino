#define AMPEREMETER_PIN  27 //
#define LED_PIN 17
#define NUMPIXELS 2

#include <WiFi.h>
#include <Adafruit_NeoPixel.h>

// Daten des WiFi-Netzwerks
//const char* ssid     = "YOUR_SSID";
//const char* password = "YOUR_PASSWORD";

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


void setup() {
  Serial.begin(115200);

  ws2812b.begin();

  gpio_set_drive_capability((gpio_num_t)AMPEREMETER_PIN, GPIO_DRIVE_CAP_0); // Set drive strength to ~10mA
  ledcSetup(ledChannel, freq, resolution);
  ledcAttachPin(AMPEREMETER_PIN, ledChannel);
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
            
            // read util and set util value
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
            // read and set color value
            if (header.indexOf("/color/") >= 0) {
              Serial.println("COLOR set");
              String color_value = header.substring(header.indexOf("/color/r/")+9);
              String r_value = color_value.substring(0, color_value.indexOf('/'));
              Serial.print("R:");
              Serial.println(r_value);
              String g_value = color_value.substring(color_value.indexOf("/g/")+3,color_value.indexOf("/b"));
              Serial.print("G:");
              Serial.println(g_value);
              String b_value = color_value.substring(color_value.indexOf("/b/")+3);
              b_value = b_value.substring(0, b_value.indexOf('/'));
              Serial.print("B:");
              Serial.println(b_value);
              ws2812b.clear();
              for(int j=0; j<NUMPIXELS; j++){
                ws2812b.setPixelColor(j, ws2812b.Color(r_value.toInt(),g_value.toInt(),b_value.toInt()));
                ws2812b.show();
              }
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