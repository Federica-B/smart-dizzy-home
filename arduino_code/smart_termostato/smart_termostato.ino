#include <LiquidCrystal.h> // includo la libreria del display lcd
const int SensorePin = A0; 
const int ledBlu = 6;
const int ledRosso = 7;
const int rele=8;
const int abbassoTemperatura = 10;
const int aumentoTemperatura = 9;
float tempGradi; 
float temperaturaMassima;
int sensorVal;
int currentStateServo;
 
LiquidCrystal lcd(12, 11, 5, 4, 3, 2); //pin display LCD
 
void setup() 
{
  Serial.begin(9600);
  pinMode(abbassoTemperatura, INPUT);
  pinMode(aumentoTemperatura, INPUT);
  pinMode(ledBlu, OUTPUT);
  pinMode(ledRosso, OUTPUT);
  pinMode(rele,OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(rele,LOW);
  analogReference(EXTERNAL);
  currentStateServo = 0; // normal temperature
  lcd.begin(16, 2);
  lcd.print("Smart");
  lcd.setCursor(0,2);
  lcd.print("thermostat");
  delay(3000);
  lcd.clear();
}
 
void loop() 
{
    //media of the values
  	for(int Ciclo = 0; Ciclo<10; Ciclo++)
      {
        sensorVal += analogRead(SensorePin);
        delay(10);
      }
    sensorVal /= 10; //esegue la media dei 10 valori letti

    tempGradi = ((sensorVal * 0.0032)-0.50) / 0.01;
  	int futureStateServo;
  	futureStateServo = currentStateServo;
  	
  	//Serial.println(tempGradi);

    
  	if (Serial.available() > 0) {
      int data = Serial.parseInt();

      if(data == 2){
        Serial.println(tempGradi);
      }

      //debugging purpose
      if(data == 1){
        digitalWrite(LED_BUILTIN,HIGH);
        }else{
          digitalWrite(LED_BUILTIN,LOW);}
        
      lcd.setCursor(0,0);
      lcd.print("Temperatura:"); // scrive sul display la parola "temperatura"
      lcd.setCursor(0,2); // sposta il cursore sulla seconda linea
      lcd.print(tempGradi); // scrive il valore in gradi della temperatura
      lcd.setCursor(6,2);
      lcd.print("degrees");

      // CASE 0: stress non detected
      if(data == 0 && currentStateServo == 0)
      {
        //Serial.println(data);
      	//Serial.println(currentStateServo);
        lcd.setCursor(0,0);
      	lcd.print("Temperatura:"); //scrive sul display la parola "temperatura"
      	lcd.setCursor(0,2); //sposta il cursore sulla seconda linea
      	lcd.print(tempGradi); //scrive il valore in gradi della temperatura
      	lcd.setCursor(6,2);
      	lcd.print("degrees");
        futureStateServo=0;
        digitalWrite(ledBlu, LOW);
        digitalWrite(ledRosso, LOW);
       }
      
      
      // CASE 1: // stress detected --> change temperature 
      if(data == 1 && currentStateServo == 0) 
      {
        //Serial.println(data);
        //Serial.println(currentStateServo);
        if(tempGradi <= 16) { // suppongo che sia inverno --> aumento
        	temperaturaMassima = tempGradi + 4; //aumento di 4 gradi
       		lcd.clear();
       		lcd.print("Temp updated: ");
       		lcd.setCursor(0,2);
       		lcd.print(temperaturaMassima);
          	lcd.setCursor(6,2);
      		lcd.print("degrees");
          	digitalWrite(ledRosso, HIGH);
        }
        if(tempGradi > 16) { // suppongo che sia estate --> diminuisco
        	temperaturaMassima = tempGradi - 4; //diminuisco di 4 gradi
       		lcd.clear();
       		lcd.print("Temp updated: ");
       		lcd.setCursor(0,2);
       		lcd.print(temperaturaMassima);
          	lcd.setCursor(6,2);
      		lcd.print("degrees");
          	digitalWrite(ledBlu, HIGH);
        }
       	delay(500);
        futureStateServo=1;
        //lcd.clear();
      }
      
     // CASE 2: stress detected & temp changed --> hold
      if(data == 1 && currentStateServo == 1) 
      {
	  	//Serial.println(data);
      	//Serial.println(currentStateServo);
      	lcd.setCursor(0,0);
      	lcd.print("Temp updated:"); //scrive sul display la parola "temperatura"
      	lcd.setCursor(0,2); //sposta il cursore sulla seconda linea
      	lcd.print(temperaturaMassima); //scrive il valore in gradi della temperatura
      	lcd.setCursor(6,2);
      	lcd.print("degrees");
     	futureStateServo=1;
        digitalWrite(ledBlu, LOW);
        digitalWrite(ledRosso, LOW);
      }
      
     // CASE 3: stress non detected & temp changed --> set normal temp
     if(data == 0 && currentStateServo == 1) // stress non detected: open windows
     {
     	//Serial.println(data);
      	//Serial.println(currentStateServo);
      	lcd.setCursor(0,0);
      	lcd.print("Temperatura:"); //scrive sul display la parola "temperatura"
      	lcd.setCursor(0,2); //sposta il cursore sulla seconda linea
      	lcd.print(tempGradi); //scrive il valore in gradi della temperatura
      	lcd.setCursor(6,2);
      	lcd.print("degrees");
        futureStateServo=0;
        digitalWrite(ledBlu, LOW);
        digitalWrite(ledRosso, LOW);
    }

        

  //output
  currentStateServo = futureStateServo;


  }

}
