#!/usr/bin/env python3
import serial
import paho.mqtt.client as mqtt
import time
import threading
import os
from typing import Tuple

from crc_package import crc
# https://www.youtube.com/watch?v=s2bH-s4LI64 -> per crc submodule directory
# devo cambiare la sintassi della comunicazione stato stress/no-stress-> {code,status,checksum}
    # [x] installare CRC -> più o meno
    # [] Fare una prima fase conoscitiva
    # [] cambiare modo in cui invia, ovvero sinstassi e anche aspettare che riceva delle informazioni 
    # [] conf file with all the codes

# Setup MQTT broker - local
broker_address = "127.0.0.1"
port = 1883
topic = "data/stress"
topic_telemetry = "telemetry/"
DEVICE_ID = "raspy"

telemetry_acm_arduino = ['/dev/ttyACM0', '/dev/ttyACM1']
# TODO: condence them in a single dict
arduino_list_serial = []
arduino_id = {}
STRESS_STATE = 0
    ## change from semaphore to lock because need binary
simp = threading.Lock()

def initilization_serial():
    try:
        arduino_serial_acmzero = serial.Serial('/dev/ttyACM0', 9600, timeout= 1)  # Su Linux/Mac
    except:
        print("Error in connecting with the serial - but the show must go on")
        arduino_list_serial.append(0)
    else:
        print("Correcly initilize the serial of "+ str(arduino_serial_acmzero.name))
        arduino_list_serial.append(arduino_serial_acmzero)
    
    try:
        arduino_serial_acmone = serial.Serial('/dev/ttyACM1', 9600, timeout= 1)  # Su Linux/Mac
    except:
        print("Error in connecting with the serial - but the show must go on")
        arduino_list_serial.append(0)
    else:
        print("Correcly initilize the serial of "+ str(arduino_serial_acmone.name))
        arduino_list_serial.append(arduino_serial_acmone)

    try:
        arduino_serial_acmtwo = serial.Serial('/dev/ttyACM2', 9600, timeout= 1)  # Su Linux/Mac
    except:
        print("Error in connecting with the serial - but the show must go on")
        arduino_list_serial.append(0)
    else:
        print("Correcly initilize the serial of "+ str(arduino_serial_acmtwo.name))
        arduino_list_serial.append(arduino_serial_acmtwo)

def controlCRC(data_list) -> bool:
    msg = str(data_list[0])+ ","+ str(data_list[1])
    b_msg= bytes(msg, 'utf-8')
    crc_reponce = crc.crc_poly(b_msg, 16, 0x8005, crc=0xFFFF, ref_in=True, ref_out=True, xor_out=0xFFFF)
    if  int(data_list[2]) == crc_reponce:
        print("Correct CRC!!")
        return True
    else:
        print("Incorrect CRC -> calculated:" + str(crc_reponce) + " recived" + str(data_list[2]))
        return False

def controlData(data) -> bool:
    data_list = []
    try:
        data_list = data.replace("{", "").replace("}","").split(",")
        if len(data_list) != 3:
            print("Message recived with NO correct syntax!")
            return False
    except IndexError as e:
        print(e)
        return False 
    except TypeError as te:
        print("Message recived with NO correct syntax!")
        print(te)
        return False
    else:
        print("Message recived with correct syntax!")

    control = controlCRC(data_list)
    if not control: return False

    if '400' == data_list[0]:
        print("Error with the CRC")
        return False
    if '401' == data_list[0]:
        print("Value string send to long - out of bound string - max axxepted 20 char")
        return False
    
    return True


def serialRequest(code_request, message, ser_arduino) -> Tuple[str,bool]:
    acquired_data = ""
    request = str(code_request)+ ","+str(message)
    msg = bytes(request, 'utf-8')
    crc_request = crc.crc_poly(msg, 16, 0x8005, crc=0xFFFF, ref_in=True, ref_out=True, xor_out=0xFFFF)
    request = bytes(str('{') + request+','+ str(crc_request)+str('}'), 'utf-8')
    print("Request send: "+ str(request))
    try:
        #until i recive MY data im going no where!!!  - Arduino UNO is slow
        counter = 0
        while len(acquired_data) < 2 or counter < 3:
            ser_arduino.write(request)
            acquired_data = ser_arduino.read_until('\x7d').decode('utf-8')
            counter = counter + 1
    except serial.SerialException as e:
        print("Something went wrong when communicating with arduino serial! - NO DATA IS READ ON THE SERIAL PORT!!!!!!")
        print(e)
        return 0
    except TypeError as e:
        print("Other stuff went wrong in the arduino communication")
        print(e)
        return 0
    else:
        print("End correclty serial communication with arduino" + str(ser_arduino.name))

    if len(acquired_data) >2:
        control = controlData(acquired_data)
    else:
        control = False
        print("No information has been reviced!")
    
    if control:
        print("Responce recived: "+ str(acquired_data))

    return acquired_data, control

def requestId() -> bool:
    for ser_arduino in arduino_list_serial:
        acquired_data = ""
        if 0 != ser_arduino:
            print("Start serial communication with arduino! - Request ID")
            acquired_data, control = settingID(ser_arduino)
            if control:
                arduino_id[ser_arduino.name] = acquired_data.replace("{", "").replace("}","").split(",")[1]
            else:
                settingID(ser_arduino)
    return control

def settingID(ser_arduino):
    code_request_id = 773
    control = True
    global DEVICE_ID
    acquired_data, control = serialRequest(code_request_id, DEVICE_ID,ser_arduino)
    return acquired_data, control

def requestSensing(ser_arduino) -> Tuple[str,bool]:
    global DEVICE_ID
    code_request_sens = 786
    control = True
    sensing_val = ""
    print("Start serial communication with arduino! - Request sensing value")
    acquired_data, control = serialRequest(code_request_sens, DEVICE_ID,ser_arduino)
    if control:
        sensing_val = acquired_data.replace("{", "").replace("}","").split(",")[1]
    return sensing_val, control

def sendStress(ser_arduino) -> Tuple[str,bool]:
    global STRESS_STATE
    code_set_stress = 883
    code_correct_stress = '283'
    control = True
    acquired_data, control = serialRequest(code_set_stress, STRESS_STATE,ser_arduino)
    if control and code_correct_stress == acquired_data.replace("{", "").replace("}","").split(",")[0] :
        print("Correcly set stress value")
    else:
        print("ENTROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        sendStress(ser_arduino)
    return acquired_data, control


def task_mqtt_stress():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected with result code " + str(rc))
            client.subscribe(topic)
        else:
            print("Failed to connect, return conde "+ str(rc))

    def on_message(client, userdata, msg):
        print("New msg arrive from topic: "+ str(topic)+ "!")
        messaggio_stress = msg.payload.decode()
        print("The value of the message is: " + str(messaggio_stress))
        if messaggio_stress == '1' or messaggio_stress == '0':
            send_data(int(messaggio_stress))
        else:
            print("Msg of stress not correct - not 0 or 1")

    def send_data(data):
        """
        Invia i dati alla porta seriale per Arduino.
        """
        global STRESS_STATE
        responce = ""
        control = True
        if(data != STRESS_STATE):
            STRESS_STATE = data
            simp.acquire()
            for ser_arduino in arduino_list_serial:
                if 0 != ser_arduino:
                    print("Start serial communication with arduino! - Set stress value")
                    _,_ = sendStress(ser_arduino)
            simp.release()
        else:
            print("No change needed to the stress value")


    print("Task MQTT assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 1: {}".format(os.getpid()))
    # MQTT Client setup
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.connect(broker_address, port)
    client.on_message = on_message
    client.loop_forever()


def sensing_mqtt_task():

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    print("Task temperature mqtt assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 2: {}".format(os.getpid()))
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.connect(broker_address, port)

    ## data initilization for telemetry
    acquire_data = ""
    control = True
    while True:
        print("Start serial communication with arduino! - Data read")
        for ser_arduino in arduino_list_serial:
            acquired_data = ""
            if 0 != ser_arduino:
                simp.acquire()
                acquired_data, control = requestSensing(ser_arduino)
                simp.release()
        
            if len(acquired_data)>1 and control:
                path = topic_telemetry + arduino_id[ser_arduino.name]
                print("The data from port: "+ str(ser_arduino.name) + " is: " + str(acquired_data))
                client.publish(path, acquired_data)
                print("Data published on topic: "+ str(path))
                    
        time.sleep(10)


def main():
    print("ID of process running main program: {}".format(os.getpid()))
 
    print("Main thread name: {}".format(threading.current_thread().name))

    initilization_serial()
    print("Serial trovate: " +str(arduino_list_serial))
    if requestId():
        print("Device ID found! - The ID found are the following:"+ str(arduino_id))
    else:
        print("Some error occured during serial communication! - The ID found are the following:"+ str(arduino_id))

    t1 = threading.Thread(target=task_mqtt_stress, name='mqtt_task_stress')
    t2 = threading.Thread(target=sensing_mqtt_task, name='sensing_mqtt_task')
    t1.start()
    t2.start()



if __name__ == "__main__":
    main()