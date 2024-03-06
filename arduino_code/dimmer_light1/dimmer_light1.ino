#include <EEPROM.h>


const int ledPin = 10;      // the pin that the LED is attached to

int brightness_max = 255;

int brightness_min = 0;   //Variable to store data read from EEPROM.

int brightness = brightness_max;   // initialize value 

void setup() {
  int eeAddress = 0;
  EEPROM.get(eeAddress, brightness_min);
  brightness_min = 20; // maybe change value in eeprom lowering
  // initialize the serial communication

  Serial.begin(9600);

  // initialize the ledPin as an output:

  pinMode(ledPin, OUTPUT);
}

void loop() {
  analogWrite(ledPin, brightness);

  // check if data has been sent from the computer:

  if (Serial.available()>0) {

    int data = Serial.parseInt();

    if(data == 1 || data == 0){ // read stress no stress
      if (data == 1){
        brightness = brightness_min;
        }else{
          brightness = brightness_max;}
         
      }else{
        //Serial.print("No valid value")
       }
    

  }
}
