#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <EEPROM.h>
#include <CRC8.h>
#include <CRC.h>

// temperature sensor
const int SensorePin = A0;
// led comunication pins
const int ledBlu = 6;
const int ledRed = 7;
PinStatus valueP = LOW;
int ledPin;
//?
// const int rele = 8;
// const int abbassoTemperatura = 10;
// const int aumentoTemperatura = 9;

// min max possible temperature
const unsigned int max_temp = 7;
const unsigned int min_temp = 0;
// current temp
float tempGradi;
float currentProjectedTemperature;
// current conf temp
unsigned int tempStress;
// used for calculation
int sensorVal;
//?
//int currentStateServo;

// state value
int state = 0;
int future_state = 0;

// address of EEPROM memory
const unsigned int eeAddress = 0;

// Set the LCD address to 0x27 or 0x3F according to your module
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Change to your LCD I2C address and size

//create new CRC istance CRC16-USB
CRC16 crc = CRC16(0x8005, 0xFFFF, 0xFFFF, true, true);
// define dataframe format
const char START_MARKER = '{';
const char END_MARKER = '}';
const char SEPARATOR = ',';

char charArray[3];
char ID_DEVICE[] = "temperature";
bool flag = false;
bool led_bool = false;

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
  uint16_t castCRCvalue = (uint16_t)crcValue;

  while (Serial.read() != END_MARKER) {}

  String dataForCRC = String(code) + "," + stringData;

  //calculate the CRC
  //uint8_t calculatedCRC = calcCRC16((const uint8_t *)dataForCRC.c_str(), dataForCRC.length(), 0x1021, 0x1D0F, 0x0000, false, false);
  crc.add((uint8_t*)dataForCRC.c_str(), dataForCRC.length());
  uint16_t calculatedCRC = crc.calc();
  crc.restart();
  //  Serial.print("Code: ");
  //  Serial.println(code);
  //  Serial.print("String: ");
  //  Serial.println(stringData);
  //  Serial.println(calculatedCRC);

  if (castCRCvalue == calculatedCRC) {
    // Data is valid

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

void serialSend(MsgStruct msg) {
  String dataForCRC = String(msg.serialCode) + "," + msg.stringValue;
  crc.add((uint8_t*)dataForCRC.c_str(), dataForCRC.length());
  uint16_t calculatedCRC = crc.calc();
  crc.restart();
  String message = String("{") + msg.serialCode + "," + String(msg.stringValue) + "," + String(calculatedCRC) + "}";
  Serial.print(message);
}

bool isNumber(const char* str) {
  for (int i = 0; str[i] != '\0'; i++) {
    if (str[i] < '0' || str[i] > '9') {
      return false;
    }
  }
  return true;
}

void displayTemp(float temp) {
  lcd.setCursor(0, 0);
  lcd.print("Temperature:");
  lcd.setCursor(0, 1);
  lcd.print(temp);
  lcd.print(" \xDF"
            "C");
}

void displayTempChanger(float temp) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Target temp:");
  lcd.setCursor(0, 1);
  lcd.print(temp);
  lcd.print(" \xDF"
            "C");
  delay(1500);
  lcd.clear();
}

MsgStruct msg;
MsgStruct responce;

void setup() {
  //EEPROM.get(eeAddress, tempStress);
  tempStress = 4;  // maybe change value in eeprom lowering

  //initilize msg struct
  msg = initializeMsgEmpty();
  responce = initializeMsgEmpty();

  // initialize the serial communication
  Serial.begin(9600);

  // initilize pin leds
  pinMode(ledBlu, OUTPUT);
  pinMode(ledRed, OUTPUT);

  lcd.init();
  lcd.backlight();  // Turn on the backlight
  lcd.print("Smart");
  lcd.setCursor(0, 1);
  lcd.print("Thermostat");
  delay(3000);

  lcd.clear();
}

void loop() {
  msg = initializeMsgEmpty();

  // display current temperature
  displayTemp(tempGradi);

  //media of the values for the temperature
  for (int Ciclo = 0; Ciclo < 10; Ciclo++) {
    sensorVal += analogRead(SensorePin);
    delay(10);
  }
  sensorVal /= 10;  //esegue la media dei 10 valori letti

  tempGradi = ((sensorVal * 0.0032) - 0.50) / 0.01;


  if (Serial.available() > 0) {
    msg = serialRead();
    flag = true;
  }

   //code control
  if (773 == msg.serialCode) {
    //get id
    //need to send a msg with the id of the device
    responce = initializeMsg(273, ID_DEVICE);

  } else if (786 == msg.serialCode) {
    // get value
    itoa(tempGradi, charArray, 10);
    responce = initializeMsg(286, charArray);

  } else if (883 == msg.serialCode) {
    // update state
    if (strcmp(msg.stringValue, "1") == 0 || strcmp(msg.stringValue, "0") == 0) {
      future_state = strtol(msg.stringValue, NULL, 10);
      responce = initializeMsg(383, msg.stringValue);
      led_bool = true;
    } else {
      responce = initializeMsg(483, msg.stringValue);
    }
  } else if (869 == msg.serialCode) {
    // update conf value
    if (isNumber(msg.stringValue))
    {
      unsigned int new_conf_value = strtoul(msg.stringValue, NULL, 10);
      if ((min_temp <= new_conf_value) && (max_temp >= new_conf_value)) {
        tempStress = new_conf_value;
        responce = initializeMsg(369, msg.stringValue);
        //EEPROM.write(eeAddress,brightness_dizzy)
      } else {
        responce = initializeMsg(469, msg.stringValue);
      }
    } else {
      responce = initializeMsg(469, msg.stringValue);
    }

  } else if (769 == msg.serialCode) {
    // get conf value
    itoa(tempStress, charArray, 10);
    responce = initializeMsg(369, charArray);

  } else if (400 == msg.serialCode || 401 == msg.serialCode) {
    // some error occured - retry communication
    responce = initializeMsg(msg.serialCode, msg.stringValue);
  } else {
    responce = initializeMsg(403, msg.stringValue);
  }

  if (future_state != state) {
    state = future_state;
    if (1 == state) {
      if (tempGradi <= 20) {
        currentProjectedTemperature = tempGradi + tempStress;
        ledPin = ledRed;
      }
      if (tempGradi > 20) {
        currentProjectedTemperature = tempGradi - tempStress;
        ledPin = ledBlu;
      }
      valueP = HIGH;
    }else{
      currentProjectedTemperature = tempGradi;
      valueP = LOW;
    }
  }
  // led to keep up (blu -> decrease) | (red -> increase)
  digitalWrite(ledPin, valueP);

  if (true == flag) {
    serialSend(responce);
    flag = false;
  }

  if(true == led_bool){
    displayTempChanger(currentProjectedTemperature);
    led_bool = false;
  }

}
