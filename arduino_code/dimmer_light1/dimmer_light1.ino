/*

  Dimmer

  Demonstrates sending data from the computer to the Arduino board, in this case

  to control the brightness of an LED. The data is sent in individual bytes,

  each of which ranges from 0 to 255. Arduino reads these bytes and uses them to

  set the brightness of the LED.

  The circuit:

  - LED attached from digital pin 9 to ground.

  - Serial connection to Processing, Max/MSP, or another serial application

  created 2006

  by David A. Mellis

  modified 30 Aug 2011

  by Tom Igoe and Scott Fitzgerald

  This example code is in the public domain.

  http://www.arduino.cchttps://www.arduino.cc/en/Tutorial/Dimmer

*/

const int ledPin = 9;      // the pin that the LED is attached to

int brightness = 0;			// initialize value 

void setup() {

  // initialize the serial communication:

  Serial.begin(9600);

  // initialize the ledPin as an output:

  pinMode(ledPin, OUTPUT);
}

void loop() {


  // check if data has been sent from the computer:

  if (Serial.available()>0) {

    // read the most recent byte (which will be from 0 to 255):

    brightness = Serial.parseInt();	 // da vedere perché ho fatto parseInt dato che con questa seriale possono mandare solo ascii
    // da vedere se nella seriale normale si possono mandare byte 
    Serial.print("Numero inserito: ");
    Serial.println(brightness, BIN);
    
    if(brightness > -1 && brightness < 256){
      Serial.print("Numero approvato: ");
      Serial.println(brightness, BIN);
       // set the brightness of the LED:
      analogWrite(ledPin, brightness);
    }

  }
}

