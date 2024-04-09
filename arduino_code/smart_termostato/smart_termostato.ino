#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const int SensorePin = A0;
const int ledBlu = 6;
const int ledRosso = 7;
const int rele = 8;
const int abbassoTemperatura = 10;
const int aumentoTemperatura = 9;
float tempGradi;
float temperaturaMassima;
int sensorVal;
int currentStateServo;


// Set the LCD address to 0x27 or 0x3F according to your module
LiquidCrystal_I2C lcd(0x27, 16, 2); // Change to your LCD I2C address and size

void displayTempChanger(float temp){

  lcd.setCursor(0, 0);
  lcd.print("Temperatura:");
  lcd.setCursor(0, 1);
  lcd.print(temp);
  lcd.print(" \xDF" "C");
  //retun 0
}

void setup()
{
  Serial.begin(9600);
  pinMode(abbassoTemperatura, INPUT);
  pinMode(aumentoTemperatura, INPUT);
  pinMode(ledBlu, OUTPUT);
  pinMode(ledRosso, OUTPUT);
  pinMode(rele, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(rele, LOW);
  //analogReference(EXTERNAL);
  currentStateServo = 0; // normal temperature

  lcd.init();
  lcd.backlight(); // Turn on the backlight
  lcd.print("Smart");
  lcd.setCursor(0, 1);
  lcd.print("Thermostat");
  delay(3000);
  
  lcd.clear();
}

void loop()
{
  //media of the values
  for (int Ciclo = 0; Ciclo < 10; Ciclo++)
  {
    sensorVal += analogRead(SensorePin);
    delay(10);
  }
  sensorVal /= 10; //esegue la media dei 10 valori letti

  tempGradi = ((sensorVal * 0.0032) - 0.50) / 0.01;
  //initilize the temperature for the display
  if (0 == currentStateServo){
    temperaturaMassima = tempGradi;
  }
  int futureStateServo;
  futureStateServo = currentStateServo;

  if (Serial.available() > 0)
  {
    int data = Serial.parseInt();

    if (data == 2)
    {
      Serial.println(tempGradi);
    }

    // CASE 0: stress non detected
    if (data == 0 && currentStateServo == 0)
    {
      futureStateServo = 0;
      digitalWrite(ledBlu, LOW);
      digitalWrite(ledRosso, LOW);
    }

    // CASE 1: stress detected --> change temperature
    if (data == 1 && currentStateServo == 0)
    {
      if (tempGradi <= 16)
      {
        temperaturaMassima = tempGradi + 4;
        digitalWrite(ledRosso, HIGH);
      }
      if (tempGradi > 16)
      {
        temperaturaMassima = tempGradi - 4;
        digitalWrite(ledBlu, HIGH);
      }
      delay(500);
      futureStateServo = 1;
    }

    // CASE 2: stress detected & temp changed --> hold
    if (data == 1 && currentStateServo == 1)
    {
      futureStateServo = 1;
      digitalWrite(ledBlu, LOW);
      digitalWrite(ledRosso, LOW);
    }

    // CASE 3: stress non detected & temp changed --> set normal temp
    if (data == 0 && currentStateServo == 1)
    {
      futureStateServo = 0;
      digitalWrite(ledBlu, LOW);
      digitalWrite(ledRosso, LOW);
    }

    //output
    currentStateServo = futureStateServo;
  }
  //display
  displayTempChanger(temperaturaMassima);
}
