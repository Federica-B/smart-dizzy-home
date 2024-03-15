#!/usr/bin/env python3
import serial
import paho.mqtt.client as mqtt
import time
import threading
import os



# Setup MQTT broker - local
broker_address = "127.0.0.1"
port = 1883
topic = "data/stress"
topic_telemetry = "telemetry/temperature"

telemetry_acm_arduino = ['/dev/ttyACM0']
arduino_list_serial = []
simp =threading.Semaphore(1)

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
        send_data(messaggio_stress)

    def send_data(data):
        """
        Invia i dati alla porta seriale per Arduino.
        """
        print("Start serial communication with arduino! - Data send")
        for ser_arduino in arduino_list_serial:
            if ser_arduino != 0:
                simp.acquire()
                try:
                    ser_arduino.write(data.encode())  # Invia il dato come stringa codificata in bytes
                    time.sleep(0.1)
                except serial.SerialException as e:
                    print("Something went wrong when communicating with arduino serial! - NO DATA IS WRITE ON THE SERIAL PORT!!!!!!")
                    print(e)
                    return 0
                except TypeError as e:
                    print("Other stuff went wrong in the arduino communication")
                    print(e)
                    return 0
                else:
                    print("End correclty serial communication with arduino" + str(ser_arduino.name))
                simp.release()


    print("Task MQTT assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 1: {}".format(os.getpid()))
    # MQTT Client setup
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.connect(broker_address, port)
    client.on_message = on_message
    client.loop_forever()


def temperature_mqtt_task():

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
    acquired_data = ""
    polling_command = '2'
    while True:
        for ser_arduino in arduino_list_serial:
            if ser_arduino != 0 and ser_arduino.port in telemetry_acm_arduino:
                print("Start serial communication with arduino! - Data read")
                simp.acquire()
                try:
                    #print(polling_command.encode())
                    ser_arduino.write(polling_command.encode())
                    acquired_data = ser_arduino.readline().decode('utf-8')
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
                simp.release()
                
                if len(acquired_data)>1:
                    acquired_data = acquired_data.split('\n')[0]
                    print("The data from port: "+ str(telemetry_acm_arduino) + " is: " + str(acquired_data))
                    client.publish(topic_telemetry, acquired_data)
                    print("Data published on topic: "+ str(topic_telemetry))
                    
        time.sleep(10)


def main():
    print("ID of process running main program: {}".format(os.getpid()))
 
    print("Main thread name: {}".format(threading.current_thread().name))

    initilization_serial()
    print("Serial trovate: " +str(arduino_list_serial))

    t1 = threading.Thread(target=task_mqtt_stress, name='mqtt_task_stress')
    t2 = threading.Thread(target=temperature_mqtt_task, name='temperature_mqtt_task')
    t1.start()
    t2.start()



if __name__ == "__main__":
    main()