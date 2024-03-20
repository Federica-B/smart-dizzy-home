# smart-dizzy-home
## Project aim
Our project aims to develop an IoT architecture that dynamically adjusts to the user's stress levels by adapting the surrounding environment. We deploied the architecture on the following hardware:

- 3 Arduino [our configuration: Arduino UNO mini, Arduino UNO R4 MINIMA, Arduino UNO R4 WIFI]
- 1 Raspberry Pi model 4B
- phone hotspot

for the dashboard we used the cloud version of [Thingsboard](https://thingsboard.io/).

## Architecture structure
### Main take away of this architecture
The core values of our architecture include scalability across diverse settings such as homes, vehicles, or offices, as well as independence from cloud reliance.
The key concept is that in each location, there's an Edge Device responsible for:
- locally performing the ML inference;
- sending the stress values to the microcontroller, which in turn carries out specific actuations;
- and bridges this collected data with the cloud.

This data can be displayed and made visible to potential caregivers, thereby integrating it into the IoT data lifecycle. The cloud can introduce and enhance numerous additional features, yet this architecture is also capable of performing effectively as a standalone system.

### A more in-depth explanation of the stack
1. A simulated **biometric device** transmits biometric data via Bluetooth to an Edge Device. This data is then sent to an appropriate local topic _data/ecg-eda_ managed by the local MQTT broker.
2. Upon publishing, this data is received by a module that **performs Machine Learning inference**. The results are then sent to another local topic _data/stress_.
3. This data is then utilized by another module responsible for **serial communication** with the Arduino, which emulates devices capable of being actuated. In our scenario, these devices include a light, a shutter, and a thermostat.
4. At the same time another module is responsable for **performinf polling** to request specific values from the actuators. This value is also sent to another local MQTT topic.
5. In the end another module subscribes to all local topics, formats the data, and then **sends it to the cloud MQTT broker**. The data received from the cloud is displayed on the Thingsboard dashboard.

### Current issues and future work
In this architecture, the actuation logic is embedded within the microcontroller's code. For example, it regulates the intensity of the dimmer light based on specific variable values stored within the code. The serial communication merely conveys predicted stress or non-stress data. We've designed the architecture to allow future adjustments in device logic. This can be achieved through functions that modify variable values stored in the EEPROM memory. Similarly, we've considered the potential for updating the machine learning model via a REST API. This involves regularly querying the cloud to check for any new models available for download and use.

### INSERT IMAGE OF THE ARCHITECTURE

## Requirements needed

  1. Arduino board (at least one)
     - Refer to Section [4: Uploading Sketch to Arduino and connecting electronic components](https://github.com/Federica-B/smart-dizzy-home/blob/main/README.md#4-upload-skatch-on-arduino-and-attach-eletric-component) to see the necessary electronic components.
  3. Suitable USB cable or optionally a 3.3V/5V level-shifter for GPIO pin connections
  4. Raspberry Pi running Ubuntu 20.04 OS or a Python 3.8 environment
  5. Local MQTT broker hosted in a Docker container or via alternative means
  6. Either a Thingsboard cloud license to use a cloud MQTT broker or the Community Edition version for local MQTT broker

For **Arduino**, you'll require the Arduino IDE to upload the sketch.
In our scenario, the **Raspberry Pi** scripts are executed on an Ubuntu 20.04 server operating system, utilizing Python version 3.8. You can download the appropriate version of the Python library from the [requirements.txt](https://github.com/Federica-B/smart-dizzy-home/blob/main/requirements.txt) file.


The serial communication between Arduino and Raspberry Pi is established through a **USB to USB-C cable**. If you decide to replicate and deploy this project, ensure that the cable you use can transmit data. Additionally, note that Arduino and Raspberry Pi operate at different voltage levels. For serial communication via GPIO pins, a 3.3V/5V level-shifter is required to safeguard the Raspberry Pi.

For MQTT to function locally, you need an **MQTT broker** operating within your local network. In our setup, we utilize a Docker container to host our local MQTT broker. If you wish to replicate this setup, you can follow this [instructions](https://github.com/sukesh-ak/setup-mosquitto-with-docker). If the broker is not hosted on the machine where you deploy the Raspberry Pi scripts, you will need to modify the scripts by changing the IP address accordingly. Additionally, if your broker has authentication requirements, you must also incorporate them into the scripts.

To enable the dashboard functionality, you must possess a **Thingboard** cloud license and obtain the token for the cloud MQTT broker. You will need to update the token within the [mqtt_local_cloud_bridge](https://github.com/Federica-B/smart-dizzy-home/blob/main/raspy/mqtt_local_cloud_bridge/mqtt_local_cloud_bridge) file, specifically in the ```c_token``` variable. If you don't have a cloud license, you can download the Community Edition and adjust the script accordingly to test the repository.

## How to use this repo
### 1. Clone the repo
You can clone the repository both in you desktop and Raspberry Pi or only in your desktop. If you chose the second option you can use ```scp``` to move the ```raspy``` directory in your Raspberry Pi using the following comand. Make sure you have ```ssh``` enable on your Raspberry Pi.

```scp -r ./smart-dizzy-home/raspy/ remote_username@10.10.0.2:/remote/directory ```

### 2. Add execute privileges
For every script in the directory [raspy_scripts](https://github.com/Federica-B/smart-dizzy-home/tree/main/raspy/raspy_scripts) you need to add execution privilages.

```chmod +x [file-name]```

### 3. Make sure you have the MQTT broker up and running 
#### &emsp; 3.1 Il you are using Docker, type the following and see if it is running.

&emsp; ```sudo doker ps```

#### &emsp; 3.2 If you have installed locally mosquitto broker, type the following and see if it is running.

&emsp; ```mosquitto```

### 4. Upload skatch on arduino and attach eletric component
In the [arduino_code](https://github.com/Federica-B/smart-dizzy-home/tree/main/arduino_code) directory, you can find all the sketches. You can also use only one Arduino, however, please note that the polling feature is only implemented in the [thermostat](https://github.com/Federica-B/smart-dizzy-home/blob/main/arduino_code/smart_termostato/smart_termostato.ino). It is recommended to test at least with this sketch.

The eletronic components need are the following:
1. Dimmer light configuration
    - 1 led
    - 330 Ohm resistor
2. Shutter configuration
    - Servo motor
3. Thermostat configuration
    - 7 segment 2 digit display
    - 1 Thermistor

The GPIO configuration of the 3 Arduino is shown in this following images.

After completing the sketch upload, connect the Arduino to the Raspberry Pi via USB. If necessary, provide power using the appropriate cable. Begin by connecting the Arduino with the thermostat sketch. Alternatively, manually modify update the variable list ```telemetry_acm_arduino``` with the appropriate ttyACM port in this [script](https://github.com/Federica-B/smart-dizzy-home/blob/main/raspy/raspy_serial_full_duplex_arduino/serial_read_write_mqtt_clients.py).

### 5. Check if the Arduinos are correctly connected
Check if the Raspberry Pi detects the Arduino correctly by using the following command.
```
dsmeg | grep ttyACM
 ```
Alternatively, you can view all the attached USB devices and their information with the following command.
  ```
usb-devices
 ```
### 6. Start the script
I recommend launching the scripts individually in separate terminals to observe each script's output in an organized manner.
```
cd smart-dizzy-home/raspy/raspy_scripts
# start machine learning module
./ML_sub.py
```
Ctrl+Alt+T
```
# new terminal - start MQTT local - cloud bridge
./mqtt_local_cloud_bridge/mqtt_local_cloud_bridge
```
Ctrl+Alt+T
```
# new terminal - start serial comunication module
./raspy_serial_full_duplex_arduino/serial_read_write_mqtt_clients.py
```
Ctrl+Alt+T
```
# new terminal - start biometric simulation device
./read_and_publish.py
```
<!-- new terminal from command line xterm -->
## Trubleshooting
- If you encounter the problem of Line Feed (LF) after moving files from Windows to Unix you can use the folling command to resolve this issue:
```
dos2unix [options] [file-name]
```
- If you do not possess three Arduinos, or if the Arduino models do not contain 'UNO' in their names, the bash script [start_simulation](https://github.com/Federica-B/smart-dizzy-home/blob/main/raspy/raspy_scripts/start_simulation) will not function. You can start the singular scripts manually.

## Future work
- [ ] Implement functionality to modify Arduino's actuation logic via serial communication by deploying a function that allows rewriting values of variables used in the actuation process. - configuration function
- [ ] Incorporate REST API functionality for model updates
- [ ] Upgrade the serial communication protocol to a standard format
