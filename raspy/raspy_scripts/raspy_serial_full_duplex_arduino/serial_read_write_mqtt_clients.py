#!/usr/bin/env python3
import serial
import paho.mqtt.client as mqtt
import time
import threading
import os
from typing import Tuple

from crc_package import crc
from code_serial_comunication import codes_serial_comunication as cs
# https://www.youtube.com/watch?v=s2bH-s4LI64 -> per crc submodule directory
# devo cambiare la sintassi della comunicazione stato stress/no-stress-> {code,status,checksum}
    # [x] installare CRC -> più o meno
    # [x] Fare una prima fase conoscitiva
    # [x] cambiare modo in cui invia, ovvero sinstassi e anche aspettare che riceva delle informazioni 
    # [] conf file with all the codes
    # [x] aggiungere thread per la configurazione
    # [] add conf logic on arduino

# Setup MQTT broker - local
broker_address = "127.0.0.1"
port = 1883
topic = "data/stress"
topic_telemetry = "telemetry/"
topic_action = "action/#"
topic_get = "get/#"
DEVICE_ID = "raspy"

telemetry_acm_arduino = ['/dev/ttyACM0', '/dev/ttyACM1']
# TODO: condence them in a single dict
arduino_list_serial = []
arduino_id = {}
STRESS_STATE = 0
COUNTER_DEAD_LOCK = 2
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
        print("Incorrect CRC -> calculated:" + str(crc_reponce) + " recived: " + str(data_list[2]))
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
        print("Value string send to long - out of bound string - max accepted 20 char")
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
    global COUNTER_DEAD_LOCK
    dl_counter = 0
    #code_response_id = '273'
    for ser_arduino in arduino_list_serial:
        acquired_data = ""
        if 0 != ser_arduino:
            print("Start serial communication with arduino! - Request ID")
            acquired_data, control = settingID(ser_arduino)
            if control and acquired_data.replace("{", "").replace("}","").split(",")[0] == cs.CORRECT_CODE_REQUEST_ID:
                arduino_id[ser_arduino.name] = acquired_data.replace("{", "").replace("}","").split(",")[1]
            elif dl_counter < COUNTER_DEAD_LOCK:
                settingID(ser_arduino)
                dl_counter = dl_counter +1
            else:
                print("Cannot confirm the correct ID because i did not recive a correct response.")
                dl_counter = 0
    return control

def settingID(ser_arduino):
    #code_request_id = 773
    control = True
    global DEVICE_ID
    acquired_data, control = serialRequest(cs.CODE_REQUEST_ID, DEVICE_ID,ser_arduino)
    return acquired_data, control

def requestSensing(ser_arduino) -> Tuple[str,bool]:
    global DEVICE_ID
    #code_request_sens = 786
    control = True
    sensing_val = ""
    print("Start serial communication with arduino! - Request sensing value")
    acquired_data, control = serialRequest(cs.CODE_REQUEST_SENS_VALUE, DEVICE_ID,ser_arduino)
    if control:
        sensing_val = acquired_data.replace("{", "").replace("}","").split(",")[1]
    return sensing_val, control

def sendStress(ser_arduino,deadlock_count = 0) -> Tuple[str,bool]:
    global STRESS_STATE, COUNTER_DEAD_LOCK
    dl_counter = deadlock_count
    #code_set_stress = 883
    #code_correct_stress = '383'
    control = True
    acquired_data, control = serialRequest(cs.CODE_UPDATE_STATE, STRESS_STATE,ser_arduino)
    if control and cs.CORRECT_CODE_UPDATE_STATE == acquired_data.replace("{", "").replace("}","").split(",")[0] :
        print("Correcly set stress value")
    elif dl_counter < COUNTER_DEAD_LOCK:
        dl_counter = dl_counter +1
        sendStress(ser_arduino, deadlock_count= dl_counter)
    else:
        print("Cannot confirm the correct actuation because i did not recive a correct response.")
        dl_counter = 0
    return acquired_data, control

def setNewConf(ser_arduino, msg, deadlock_count = 0) -> Tuple[str,bool]:
    global COUNTER_DEAD_LOCK
    dl_counter = deadlock_count
    #code_set_new_value = 869
    #code_correct_new_value = '369'
    control = True
    acquired_data, control = serialRequest(cs.CODE_UPDATE_CONF_VALUE, msg,ser_arduino)
    if control and cs.CORRECT_CODE_UPDATE_CONF_VALUE == acquired_data.replace("{", "").replace("}","").split(",")[0] :
        print("Correcly set new conf value")
    elif dl_counter < COUNTER_DEAD_LOCK:
        dl_counter = dl_counter +1
        setNewConf(ser_arduino, msg, deadlock_count= dl_counter)
    else:
        print("Cannot confirm the correct new conf value because i did not recive a correct response.")
        dl_counter = 0
    return acquired_data, control

def getConfValueS(ser_arduino)-> Tuple[str,bool]:
    #code_request_conf = 769
    control = True
    global DEVICE_ID
    acquired_data, control = serialRequest(cs.CODE_REQUEST_CONF_VALUE, DEVICE_ID,ser_arduino)
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

def set_conf_value_mqtt_task():

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected with result code " + str(rc))
            client.subscribe(topic_action)
        else:
            print("Failed to connect, return conde "+ str(rc))


    def on_message(client, userdata, msg):
        msg_topic = str(msg._topic)
        msg_action = msg.payload.decode()
        print("New msg arrive from topic: "+ str(msg_topic)+ "!")
        print("The value of the message is: " + str(msg_action))
        list_id = []
        [list_id.append(v) for v in arduino_id.values()]
        if msg_topic.replace('\'','').split('/')[-1] in list_id and msg_action.isdigit():
            value_msg = int(msg_action)
            if value_msg < 0: value_msg = value_msg*-1
            try:
                port = [k for k,v in arduino_id.items() if v == msg_topic.replace('\'','').split('/')[-1]]
            except TypeError as e:
                print(e)

            if len(port) == 0:
                print("No match found for topic and serial port")
            else:
                sendNewConfValue(port[0], value_msg)


    def sendNewConfValue(port, value):
        acquired_data = ""
        control = True
        for ser_arduino in arduino_list_serial:
            if ser_arduino != 0 and ser_arduino.name == port:
                print("Start serial communication with arduino! - Set new conf value")
                simp.acquire()
                acquired_data,control= setNewConf(ser_arduino, value)
                simp.release()
                if len(acquired_data)>1 and control:
                    print("New data set to: "+ str(acquired_data.replace("{", "").replace("}","").split(",")[1]))


    print("Task temperature mqtt assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 3: {}".format(os.getpid()))
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.connect(broker_address, port)
    client.on_message = on_message
    client.loop_forever()

def get_conf_value_mqtt_task():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected with result code " + str(rc))
            client.subscribe(topic_get)
        else:
            print("Failed to connect, return conde "+ str(rc))


    def on_message(client, userdata, msg):
        msg_topic = str(msg._topic)
        msg_get = msg.payload.decode()
        print("New msg arrive from topic: "+ str(msg_topic)+ "!")
        print("The value of the message is: " + str(msg_get))
        list_id = []
        port =[]
        [list_id.append(v) for v in arduino_id.values()]
        if msg_topic.replace('\'','').split('/')[-1] in list_id and msg_get.isdigit():
            value_msg = int(msg_get)
            if value_msg < 0: value_msg = value_msg*-1
            try:
                port = [k for k,v in arduino_id.items() if v == msg_topic.replace('\'','').split('/')[-1]]
            except TypeError as e:
                print(e)

            if len(port) == 0:
                print("No match found for topic and serial port")
            else:
                getConfValue(port[0])

    def getConfValue(port):
        acquired_data = ""
        control = True
        for ser_arduino in arduino_list_serial:
            if ser_arduino != 0 and ser_arduino.name == port:
                print("Start serial communication with arduino! - Get conf value")
                simp.acquire()
                acquired_data,control= getConfValueS(ser_arduino)
                simp.release()
                if len(acquired_data)>1 and control:
                    print("Value of conf: "+ str(acquired_data.replace("{", "").replace("}","").split(",")[1]))

    print("Task temperature mqtt assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 4: {}".format(os.getpid()))
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.connect(broker_address, port)
    client.on_message = on_message
    client.loop_forever()

    

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
    t3 = threading.Thread(target=set_conf_value_mqtt_task, name = 'set_conf_value_mqtt_task')
    t4 = threading.Thread(target = get_conf_value_mqtt_task, name ='get_conf_value_mqtt_task')
    t1.start()
    t2.start()
    t3.start()
    t4.start()



if __name__ == "__main__":
    main()