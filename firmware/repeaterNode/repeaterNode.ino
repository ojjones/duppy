// Example sketch showing how to send in OneWire temperature readings
#include <MySensor.h>
#include <mq135.h>
#include <adc.h>
#include <SPI.h>
#include <DallasTemperature.h>
#include <OneWire.h>

#define MQ135_PULLDOWNRES 21370

#define DS18_ID 0
#define MQ135_ID 2

#define ONE_WIRE_BUS A5 // Pin where dallase sensor is connected 
#define MAX_ATTACHED_DS18B20 16
unsigned long SLEEP_TIME = 3000; // Sleep time between reads (in milliseconds)
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
MySensor gw;
float lastTemperature[MAX_ATTACHED_DS18B20];
int numSensors=0;
boolean receivedConfig = false;
boolean metric = true; 
// Initialize temperature message
MyMessage ds18_msg(DS18_ID,V_TEMP);
MyMessage mq135_msg(MQ135_ID, V_VAR1);

int sensorPin = A0;

void setup()  
{ 
  // Startup OneWire 
  sensors.begin();
  
  // Init ADC
  adc_init();

  // Startup and initialize MySensors library. Set callback for incoming messages. 
  gw.begin(); 

  // Send the sketch version information to the gateway and Controller
  gw.sendSketchInfo("Temperature Sensor", "1.0");

  // Fetch the number of attached temperature sensors  
  numSensors = sensors.getDeviceCount();

  // Present all sensors to controller
  for (int i=0; i<numSensors && i<MAX_ATTACHED_DS18B20; i++) {   
     gw.present(i, S_TEMP);
  }
}

long readMq135() {
  long adc = 0;
  long res = 0;
  long mq135_ro = 0;
  long d = 0;
  
  // read the value from the sensor:
  adc = analogRead(sensorPin);
  Serial.print("A0: ");
  Serial.println(adc);
  res = adc_getresistence(adc, MQ135_PULLDOWNRES);
  mq135_ro = mq135_getro(res, MQ135_DEFAULTPPM);
  d = mq135_getppm(res, MQ135_DEFAULTRO);
  Serial.print("C02: ");
  Serial.println(d);
  
  return d;
}

void loop()     
{ 
  long co2 = 0;  
  // Process incoming messages (like config from server)
  gw.process(); 

  // Fetch temperatures from Dallas sensors
  sensors.requestTemperatures(); 
  
  co2 = readMq135();
  gw.send(mq135_msg.set(co2));

  // Read temperatures and send them to controller 
  for (int i=0; i<numSensors && i<MAX_ATTACHED_DS18B20; i++) {
 
    // Fetch and round temperature to one decimal
    float temperature = static_cast<float>(static_cast<int>((gw.getConfig().isMetric?sensors.getTempCByIndex(i):sensors.getTempFByIndex(i)) * 10.)) / 10.;
    // Only send data if temperature has changed and no error
    //if (lastTemperature[i] != temperature && temperature != -127.00) {
      
      // Send in the new temperature
      gw.send(ds18_msg.setSensor(i).set(temperature,1));
      lastTemperature[i]=temperature;
    //}
  }
  
  gw.sleep(SLEEP_TIME);
}




