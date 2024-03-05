#include <Servo.h>

/*
  ARDUINO MOTOR SERVO
  
  Obiettivo: lo script di attuazione nel raspb. pi invierà un segnale di
             attuazione in caso di stress per chiudere le finestre (inclinazione
             delle tapparelle di esempio 45°)

  Stress detected --> close windows 
  Stress non detected --> hold

  States:
   - 0: windows open == stress non detected
   - 1: windows closed == stress detected


*/

int pos=30;
int currentStateServo;

Servo servo;

void setup(){
  Serial.begin(9600);
  servo.attach(9,500, 2500); 
  
  currentStateServo = 0; // windows open
}
void loop(){
  servo.write(pos); // shutter open
  // default: future state = current state
  int futureStateServo;
  futureStateServo = currentStateServo;
  
  if (Serial.available() > 0) { //if data flows
    int data = Serial.parseInt();
 
    // CASE 0: stress non detected & windows open --> hold
    if(data == 0 && currentStateServo == 0){
      Serial.println(data);
      Serial.println(currentStateServo);
      futureStateServo=0;
      pos=30;
    }
    
    // CASE 1: // stress detected & windows open --> close 
    if(data == 1 && currentStateServo == 0) 
	{
      Serial.println(data);
      Serial.println(currentStateServo);
      for (int i = 30; i >= 0; i -= 1) {
        // servo closes windows
        servo.write(i);
        delay(100);
      }
      futureStateServo=1;
      pos=0;
    }
    
    // CASE 2: stress detected & windows closed --> hold
    if(data == 1 && currentStateServo == 1) {
	  Serial.println(data);
      Serial.println(currentStateServo);
      futureStateServo=1; 
      pos=0;
    }

    // CASE 3: stress non detected & windows closed --> open
    if(data == 0 && currentStateServo == 1) // stress non detected: open windows
    {
      Serial.println(data);
      Serial.println(currentStateServo);
      for (int i = 0; i <= 30; i += 1) {
        // tell servo to go to position in variable 'pos'
        servo.write(i);
        delay(100);
      }
      futureStateServo=0; 
      pos=30;
    }
    
    // change future state in current state
    if(futureStateServo != currentStateServo) {
      if(futureStateServo == 0) servo.write(0);
	  if(futureStateServo == 1) servo.write(30);
  	}

  //output
  currentStateServo = futureStateServo;
  }
}