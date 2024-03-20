# smart-dizzy-home
## Project aim
Our project aims to develop an IoT architecture that dynamically adjusts to the user's stress levels by adapting the surrounding environment. We deploied the architecture on the following hardware:

- 3 Arduino [our configuration: Arduino UNO mini, Arduino UNO R4 MINIMA, Arduino UNO R4 WIFI]
- 1 Raspberry Pi model 4B
- phone hotspot

for the dashboard we used the cloud version of [Thingsboard](https://thingsboard.io/).

## Architecture structure
A simulated biometric device transmits biometric data via Bluetooth to an Edge Device (in our case simulated by the Raspberry Pi). This data is then sent to an appropriate local topic _data/ecg-eda_ managed by the local MQTT broker. Upon publishing, this data is received by a module that performs Machine Learning inference. The results are then sent to another local topic _data/stress_. This data is then utilized by another module responsible for serial communication with the Arduino, which emulates devices capable of being actuated. In our scenario, these devices include a light, a shutter, and a thermostat. At the same time another module is responsable for performinf polling to request specific values from the actuator. This value is also sent to another local MQTT topic. In the end another module subscribes to all local topics, formats the data, and then sends it to the cloud MQTT broker. The data received from the cloud is displayed on the Thingsboard dashboard.

We believe this architecture can be scalable across various settings, such as vehicles or offices, where different types of actuation can occur in response to stress. The key concept is that in each location, there's an Edge Device responsible for:
- locally performing the ML inference
- sending the stress values to the microcontroller, which in turn carries out specific actuations
- and bridges this collected data with the cloud.
This data can be displayed and made visible to potential caregivers, thereby integrating it into the IoT data lifecycle.

In this architecture, the actuation logic is embedded within the microcontroller's code. For example, it regulates the intensity of the dimmer light based on specific variable values stored within the code. The serial communication merely conveys predicted stress or non-stress data. We've designed the architecture to allow future adjustments in device logic. This can be achieved through functions that modify variable values stored in the EEPROM memory. Similarly, we've considered the potential for updating the machine learning model via a REST API. This involves regularly querying the cloud to check for any new models available for download and use.

### INSERT IMAGE OF THE ARCHITECTURE

## Requirements needed

  1. Arduino board (at least one)
  2. Suitable USB cable or optionally a 3.3V/5V level-shifter for GPIO pin connections
  3. Raspberry Pi running Ubuntu 20.04 OS or a Python 3.8 environment
  4. Local MQTT broker hosted in a Docker container or via alternative means
  5. Either a Thingsboard cloud license to use a cloud MQTT broker or the Community Edition version for local MQTT broker

For **Arduino**, you'll require the Arduino IDE to upload the sketch.
In our scenario, the **Raspberry Pi** scripts are executed on an Ubuntu 20.04 server operating system, utilizing Python version 3.8. You can download the appropriate version of the Python library from the [requirements.txt](https://github.com/Federica-B/smart-dizzy-home/blob/main/requirements.txt) file.


The serial communication between Arduino and Raspberry Pi is established through a **USB to USB-C cable**. If you decide to replicate and deploy this project, ensure that the cable you use can transmit data. Additionally, note that Arduino and Raspberry Pi operate at different voltage levels. For serial communication via GPIO pins, a 3.3V/5V level-shifter is required to safeguard the Raspberry Pi.

For MQTT to function locally, you need an **MQTT broker** operating within your local network. In our setup, we utilize a Docker container to host our local MQTT broker. If you wish to replicate this setup, you can follow this [instructions](https://github.com/sukesh-ak/setup-mosquitto-with-docker). If the broker is not hosted on the machine where you deploy the Raspberry Pi scripts, you will need to modify the scripts by changing the IP address accordingly. Additionally, if your broker has authentication requirements, you must also incorporate them into the scripts.

To enable the dashboard functionality, you must possess a **Thingboard** cloud license and obtain the token for the cloud MQTT broker. You will need to update the token within the [mqtt_local_cloud_bridge](https://github.com/Federica-B/smart-dizzy-home/blob/main/raspy/mqtt_local_cloud_bridge/mqtt_local_cloud_bridge) file, specifically in the ```c_token``` variableThe token has to be changed in the file. If you don't have a cloud license, you can download the Community Edition and adjust the script accordingly to test the repository.

## Trubleshooting
- If you encounter the problem of Line Feed after moving files from Windows to Unix you can use the folling command to resolve this issue:
```
dos2unix [options] [file-name]
```
- If you do not possess three Arduinos, or if the Arduino models do not contain 'UNO' in their names, the bash script [start_simulation](https://github.com/Federica-B/smart-dizzy-home/blob/main/raspy/raspy_scripts/start_simulation) will not function. You can start the singular scrips manually.
