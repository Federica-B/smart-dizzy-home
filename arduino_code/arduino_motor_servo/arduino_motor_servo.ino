#include <Servo.h>
#include <EEPROM.h>
#include <CRC8.h>
#include <CRC.h>

/*
  ARDUINO MOTOR SERVO

  Obiettivo: lo script di attuazione nel raspb. pi invierà un segnale di
             attuazione in caso di stress per chiudere le finestre

  Stress detected --> close windows
  Stress non detected --> hold

  States:
   - 0: windows open == stress non detected
   - 1: windows closed == stress detected


*/

int pos;
int temp_shutter;
int target_shutter;
int temp;

int state = 0;
int future_state = 0;

const unsigned int eeAddress = 0;
const int max_shutter = 90;
const int min_shutter = 30;
const unsigned int START_POSE = 100;

//create new CRC istance CRC16-USB
CRC16 crc = CRC16(0x8005, 0xFFFF, 0xFFFF, true, true);
// define dataframe format
const char START_MARKER = '{';
const char END_MARKER = '}';
const char SEPARATOR = ',';

char charArray[4];
char ID_DEVICE[] = "shutter";
bool flag = false;

Servo servo;
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
  uint16_t castCRCvalue = (uint16_t) crcValue;

  while (Serial.read() != END_MARKER) {}

  String dataForCRC = String(code) + "," + stringData;

  //calculate the CRC
  //uint8_t calculatedCRC = calcCRC16((const uint8_t *)dataForCRC.c_str(), dataForCRC.length(), 0x1021, 0x1D0F, 0x0000, false, false);
  crc.add((uint8_t*)dataForCRC.c_str(), dataForCRC.length());
  uint16_t calculatedCRC = crc.calc();
  crc.restart();
  //Serial.print("Code: ");
  //Serial.println(code);
  //Serial.print("String: ");
  //Serial.println(stringData);
  //Serial.println(calculatedCRC);

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

void openCloseBlinds(int current, int target) {
  if (current > target) {
    for (int i = current ; i >= target; i -= 1) {
      // tell servo to go to position in variable 'pos'
      servo.write(i);
      delay(10);
    }
  }else{
      for (int i = current ; i <= target; i += 1) {
      // tell servo to go to position in variable 'pos'
      servo.write(i);
      delay(10);
  }}
}

bool isNumber(const char* str) {
  for (int i = 0; str[i] != '\0'; i++) {
    if (str[i] < '0' || str[i] > '9') {
      return false;
    }
  }
  return true;
}

MsgStruct msg;
MsgStruct responce;


void setup() {
  //EEPROM.get(eeAddress, pos);
  pos = 30;  // maybe change value in eeprom lowering
  // initialize the serial communication

  msg = initializeMsgEmpty();
  responce = initializeMsgEmpty();

  Serial.begin(9600);
  servo.attach(9, 9500, 2500);

  target_shutter = 100;
  servo.write(START_POSE); //shutter open
}
void loop() {
  msg = initializeMsgEmpty();

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
    itoa(target_shutter, charArray, 10);
    responce = initializeMsg(286, charArray);

  } else if (883 == msg.serialCode) {
    // update state
    if (strcmp(msg.stringValue, "1") == 0 || strcmp(msg.stringValue, "0") == 0) {
      future_state = strtol(msg.stringValue, NULL, 10);
      responce = initializeMsg(383, msg.stringValue);
    } else {
      responce = initializeMsg(483, msg.stringValue);
    }
  } else if (869 == msg.serialCode) {
    // update conf value
    if (isNumber(msg.stringValue))
    {
      int new_conf_value = strtoul(msg.stringValue, NULL, 10);
      if ((min_shutter <= new_conf_value) && (max_shutter >= new_conf_value)) {
        pos = new_conf_value;
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
    itoa(pos, charArray, 10);
    responce = initializeMsg(369, charArray);

  } else if (400 == msg.serialCode || 401 == msg.serialCode) {
    // some error occured - retry communication
    responce = initializeMsg(msg.serialCode, msg.stringValue);
  } else {
    responce = initializeMsg(403, msg.stringValue);
  }

  if (true == flag) {
    serialSend(responce);
    flag = false;
  }

  if (future_state != state) {
    state = future_state;
    if (1 == state) {
      temp_shutter = target_shutter;
      target_shutter = pos;
      openCloseBlinds(temp_shutter, target_shutter);
    } else {
      
      temp = target_shutter;
      target_shutter = temp_shutter;
      openCloseBlinds(temp, target_shutter);
    }
  }
  
  //servo.write(target_shutter);

}
