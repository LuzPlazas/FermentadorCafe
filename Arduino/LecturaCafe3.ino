#include <OneWire.h>
#include <DallasTemperature.h>
#include <movingAvg.h>

#define pinA 7
#define pinB 6

int sensorAlcohol = 0;
int sensorPH = 0;
int PHfiltrado = 0;
int sensorTDS = 0;
int TDSfiltrado = 0;
int sensorCO2 = 0;
float Temp1=0;
float Temp2=0;
byte perfilA=0;
byte perfilB=0;
int datoPerfil=0;

//

long PorcAl =0;

// GPIO where the DS18B20 is connected to
const int oneWireBus = 9;
const int twoWireBus = 10; 

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(oneWireBus);
OneWire twoWire(twoWireBus);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensorT1(&oneWire);
DallasTemperature sensorT2(&twoWire);
//
float EMA_ALPHA = 0.2;//MENOR ES EL NUMERO MAYOR FILTRADO Y ATENUACIÓN
float EMA_LP = 0;
//
float EMA_ALPHA2 = 0.5;//MENOR ES EL NUMERO MAYOR FILTRADO Y ATENUACIÓN
float EMA_LP2 = 0;

//
//long SampleTime = 60000; //ms
long SampleTime = 5000; //ms
//long SampleTime = 30000; //ms
unsigned long lastTime = 0;


//moving average para ph
movingAvg avgPH(200);  

void setup() {
  // put your setup code here, to run once:
  Serial.begin(19200);  //9600 19200 o 115200
  pinMode(13, OUTPUT);
  digitalWrite(7, LOW); 
  pinMode(pinA, INPUT);//perfilA
  pinMode(pinB, INPUT);//perfilB

  
  // Start the DS18B20 sensor
  sensorT1.begin();//inicias el sensor de temp1
  sensorT1.setResolution(12);
  sensorT2.begin();
  sensorT2.setResolution(12);

   avgPH.begin();                            // initialize the moving average
}

void loop() {


  if (datoPerfil==0)
  {
  selectPerfil();
  }
  
  sensorTDS = analogRead(A0);
  sensorCO2 = analogRead(A1);
  sensorAlcohol = analogRead(A2);
  sensorPH = analogRead(A3);

  TDSfiltrado = EMALowPassFilter2(sensorTDS);

  PHfiltrado  = avgPH.reading(sensorPH); 
  ReadDS18B20();
  unsigned long now = millis();
  long timeChange = (now - lastTime);


  // Determina si hay que ejecutar el PID o retornar de la función.
  if (timeChange >= SampleTime)
  {  
   Serial.println(String(TDSfiltrado)+","+String(sensorCO2)+","+String(sensorAlcohol)+","+String(PHfiltrado)+","+String(Temp1)+","+String(Temp2)+","+String(datoPerfil));
   lastTime = now;
  }
}

// Lectura Temperaturas
void ReadDS18B20()
{
  sensorT1.requestTemperatures(); 
  Temp1 = sensorT1.getTempCByIndex(0);
  //Serial.print(temperatureC);
  //Serial.println("ºC");
  delay(2000);//retardo ms
  
  sensorT2.requestTemperatures(); 
  Temp2 = sensorT2.getTempCByIndex(0);
  Temp2= Temp2-1;
  //Serial.print(temperatureC_2);
  //Serial.println("ºC");
  delay(2000);//retardo ms
}
void selectPerfil(){
  perfilA = digitalRead(pinA);
  perfilB = digitalRead(pinB);
  
  if(perfilA==0 && perfilB==0)
    datoPerfil = 0;
  else if(perfilA==0 && perfilB==1)
    datoPerfil = 1;
  else if(perfilA==1 && perfilB==0)
    datoPerfil = 2;
  else if(perfilA==1 && perfilB==1)
    datoPerfil = 3;    
}

//FUNCION FILTRADO
float EMALowPassFilter(float value)
{
  EMA_LP = EMA_ALPHA * value + (1 - EMA_ALPHA) * EMA_LP;
  return EMA_LP;
}

float EMALowPassFilter2(float value)
{
  EMA_LP2 = EMA_ALPHA2 * value + (1 - EMA_ALPHA2) * EMA_LP2;
  return EMA_LP2;
}
