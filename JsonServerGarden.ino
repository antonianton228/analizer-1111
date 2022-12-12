#include "Arduino.h" //так как у нас нестандартный модуль 
#include <ESP8266WiFi.h>//чтоб работал интернет
#include <WiFiClient.h>// чтоб создать сервер
#include <ESP8266WebServer.h>//
#include <ESP8266mDNS.h>//
#include <OneWire.h>// для правильного считывания датчика
#include <DallasTemperature.h>// для датчика температуры
const int SensorDataPin = 14;
constexpr auto pinSensor = A0;
      
OneWire oneWire(SensorDataPin); //подключаем датчик влажности к библиотеке 6
 
DallasTemperature sensors(&oneWire);// в экземпляр класса библиотеке 7 передаем экземпляр класс библеотеки 6, тем самым подключая температуру
const char* ssid = "iPhone (2)";
const char* password = "12345678";
 
ESP8266WebServer server(80);// создаем сервер который распологается на локальном IP адресе в парту 80
 
// Serving Hello world
void getHelloWord() {
    server.send(200, "text/json", "{\"Temperature\": \"" + getTemp() + "\", \"Humidity\":\""+getHumidity()+"\"}");
}

String getTemp(){ //  функция которая возвращает температуру
    sensors.requestTemperatures(); // сообщаем библ что будем к ней обращаться, обновления данных
  float temperature_Celsius = sensors.getTempCByIndex(0);//обращаемся к информации по индексу 0 градусу по цельсию
  return String(temperature_Celsius);//возвращаем показатели
}

String getHumidity(){ // функция которая возврвщвем влажность
  int valueSensor = analogRead(pinSensor);// считываем аналоговые даные которые лежат в пинсенсор
  return String(valueSensor);// возвращаем  показатели
}
// Serving Hello world
void getSettings() { // настраиваем сервер
    String response = "{";// создаем пустую строчку
 
    response+= "\"ip\": \""+WiFi.localIP().toString()+"\"";// добавляем локальный ip в джейсонку
    response+= ",\"gw\": \""+WiFi.gatewayIP().toString()+"\"";// ip для всех устройсв которые поудключены к этому роутеру
    response+= ",\"nm\": \""+WiFi.subnetMask().toString()+"\"";//ip для безопасности, получаем маску
 
    if (server.arg("signalStrength")== "true"){//если сервер запущен в определенном режиме то добовляем значения
        response+= ",\"signalStrengh\": \""+String(WiFi.RSSI())+"\"";
    }
 
    if (server.arg("chipInfo")== "true"){
        response+= ",\"chipId\": \""+String(ESP.getChipId())+"\"";
        response+= ",\"flashChipId\": \""+String(ESP.getFlashChipId())+"\"";
        response+= ",\"flashChipSize\": \""+String(ESP.getFlashChipSize())+"\"";
        response+= ",\"flashChipRealSize\": \""+String(ESP.getFlashChipRealSize())+"\"";
    }
    if (server.arg("freeHeap")== "true"){
        response+= ",\"freeHeap\": \""+String(ESP.getFreeHeap())+"\"";
    }
    response+="}";
 
    server.send(200, "text/json", response);// всю информацию записвыем на сервер
}
 
// Define routing//функция делает так чтобы с сервера получалась инфа, общенея сервера с клиентом
void restServerRouting() {//создаем функц
    server.on("/", HTTP_GET, []() {//гл стр сервера
        server.send(200, F("text/html"),
            F("Welcome to the REST Web Server"));//отправляем штимельку в которой написано читай слево
    });
    server.on(F("/helloWorld"), HTTP_GET, getHelloWord);//если чел на хелоу ворд то ему выведятся значения с функции гет хеллоу ворд
    server.on(F("/settings"), HTTP_GET, getSettings);// инф о сервере Ip и тд
}
 
// Manage not found URL
void handleNotFound() {//эта функция обрабатывает ошибку, если зайдешь на несуществующею стр ошибка 404
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}
 
void setup(void) {//инициализируется функция 
  Serial.begin(115200);//создаем порт для общения компа с платой
  sensors.begin();//инциализируем датчики
  WiFi.mode(WIFI_STA);//установка нужного режима работы вайфая
  WiFi.begin(ssid, password);//стартуем работу
  Serial.println("");//выводим пустую строку в последовательный порт
 
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");//цикл который проверяет подкл ли вайфай, если нет принт точка, если да выодим ip адрес нашего сервера
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
 
  // Activate mDNS this is used to be able to connect to the server
  // with local DNS hostmane esp8266.local
  if (MDNS.begin("esp8266")) {//если создался сервер пишеи ответчик создан, серер который отправляет данные заработал
    Serial.println("MDNS responder started");
  }
 
  // Set server routing
  restServerRouting();
  // Set not found response
  server.onNotFound(handleNotFound);
  // Start server
  server.begin();
  Serial.println("HTTP server started");
} // инциализируем сервер
 
void loop(void) {
  server.handleClient();
}//каждую секунду выполняется код, смотри подключился ли клиен
