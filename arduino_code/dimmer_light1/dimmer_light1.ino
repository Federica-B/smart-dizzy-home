#include <EEPROM.h>
#include <CRC8.h>
#include <CRC.h>

const int ledPin = 10;  // the pin that the LED is attached to
int brightness_dizzy = 0;
int temp_brightness = 0;           //Variable to store data read from EEPROM.
int brightness = 255;  // initialize value
int state = 0;
int future_state = 0;

//create new CRC istance CRC16-USB
CRC16 crc = CRC16(0x8005, 0xFFFF, 0xFFFF, true, true);
// define dataframe format
const char START_MARKER = '{';
const char END_MARKER = '}';
const char SEPARATOR = ',';

char charArray[3];
char ID_DEVICE[] = "light";
bool flag = false;

typedef struct {
  int serialCode;
  char stringValue[20];
} MsgStruct;

MsgStruct initializeMsgEmpty() {
  MsgStruct msg;
  msg.serialCode = 0;
  memset(msg.stringValue, ' ', sizeof(msg.stringValue));
  return msg;
}

MsgStruct initializeMsg(int code, char value[20]) {
  MsgStruct msg;
  msg.serialCode = code;
  strncpy(msg.stringValue, value, sizeof(msg.stringValue));
  return msg;
}

MsgStruct serialRead() {
  MsgStruct msg;

  //read characters until the start marker is found
  while (Serial.read() != START_MARKER) {}

  int code = Serial.parseInt();

  while (Serial.read() != SEPARATOR) {}

  String stringData = Serial.readStringUntil(SEPARATOR);

  //Read the CRC
  int crcValue = Serial.parseInt();

  while (Serial.read() != END_MARKER) {}

  String dataForCRC = String(code) + "," + stringData;

  //calculate the CRC
  //uint8_t calculatedCRC = calcCRC16((const uint8_t *)dataForCRC.c_str(), dataForCRC.length(), 0x1021, 0x1D0F, 0x0000, false, false);
  crc.add((uint8_t*)dataForCRC.c_str(), dataForCRC.length());
  int calculatedCRC = crc.calc();
  // Serial.println(calculatedCRC);
  crc.restart();

  if (crcValue == calculatedCRC) {
    // Data is valid
    // Serial.print("Code: ");
    // Serial.println(code);
    // Serial.print("String: ");
    // Serial.println(stringData);

    msg.serialCode = code;
    if (20 >= stringData.length()) {
      stringData.toCharArray(msg.stringValue, sizeof(msg.stringValue));
    } else {
      // serial error - outofbound array value
      msg.serialCode = 401;
      stringData.toCharArray(msg.stringValue, sizeof(msg.stringValue));
    }
  } else {
    // CRC mismatch
    // CRC error - mismatch
    msg.serialCode = 400;
    stringData.toCharArray(msg.stringValue, sizeof(msg.stringValue));
    // Serial.println("CRC Error");
  }

  return msg;
}

void serialSend(MsgStruct msg){
  String dataForCRC = String(msg.serialCode) + "," + msg.stringValue; 
  crc.add((uint8_t*)dataForCRC.c_str(), dataForCRC.length());
  int calculatedCRC = crc.calc();
  crc.restart();
  String message = String("{") + msg.serialCode + "," + String(msg.stringValue) + "," + String(calculatedCRC) + "}";
  Serial.print(message);
}

MsgStruct msg;
MsgStruct responce;


void setup() {
  //int eeAddress = 0;
  //EEPROM.get(eeAddress, brightness_dizzy);
  brightness_dizzy = 20;  // maybe change value in eeprom lowering
  // initialize the serial communication


  msg = initializeMsgEmpty();
  responce = initializeMsgEmpty();

  Serial.begin(9600);


  // initialize the ledPin as an output:

  pinMode(ledPin, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  msg = initializeMsgEmpty();

  if(future_state != state){
    state = future_state;
    if(1 == state){
      temp_brightness = brightness;
      brightness = brightness_dizzy;
    }else{
      brightness = temp_brightness;
    }
  }

  analogWrite(ledPin, brightness);

  // check if data has been sent from the computer:
  if (Serial.available() > 0) {
    msg = serialRead();
    flag = true;
  }

  //code control
  if (773 == msg.serialCode) {
    //get id
    //need to send a msg with the id of the device
    responce = initializeMsg(273, ID_DEVICE);

  }else if(786 == msg.serialCode){
    // get value
    itoa(brightness, charArray, 10);
    responce = initializeMsg(286, charArray);

  }else if(883 == msg.serialCode){
    // update state
     if(strcmp(msg.stringValue, "1") == 0 || strcmp(msg.stringValue, "0") == 0){
      future_state = atoi(msg.stringValue);
      responce = initializeMsg(283, msg.stringValue);
     }else{
      responce = initializeMsg(483, msg.stringValue);
     }
  }else if(869 == msg.serialCode){
    responce = initializeMsg(269, msg.stringValue);

  }else if(400 == msg.serialCode || 401 == msg.serialCode){
    // some error occured - retry communication
    responce = initializeMsg(msg.serialCode, msg.stringValue);
  }

  if (true == flag){
    serialSend(responce);
    flag = false;
  }
}
