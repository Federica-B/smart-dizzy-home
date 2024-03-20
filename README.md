# smart-dizzy-home
## Project aim
Our project aims to develop an IoT architecture that dynamically adjusts to the user's stress levels by adapting the surrounding environment. We deploied the architecture on the following hardware:

- 3 Arduino [our configuration: Arduino UNO mini, Arduino UNO R4 MINIMA, Arduino UNO R4 WIFI]
- 1 Raspberry Pi model 4B
- phone hotspot

for the dashboard we used the cloud version of [Thingsboard](https://thingsboard.io/).

## Requirements needed

For **Arduino**, you'll require the Arduino IDE to upload the sketch.
In our scenario, the **Raspberry Pi** scripts are executed on an Ubuntu 20.04 server operating system, utilizing Python version 3.8. You can download the appropriate version of the Python library from the [requirements.txt](https://github.com/Federica-B/smart-dizzy-home/blob/main/requirements.txt) file.


The serial communication between Arduino and Raspberry Pi is established through a **USB to USB-C cable**. If you decide to replicate and deploy this project, ensure that the cable you use can transmit data. Additionally, note that Arduino and Raspberry Pi operate at different voltage levels. For serial communication via GPIO pins, a 3.3V/5V level-shifter is required to safeguard the Raspberry Pi.

For MQTT to function locally, you need an **MQTT broker** operating within your local network. In our setup, we utilize a Docker container to host our local MQTT broker. If you wish to replicate this setup, you can follow this [instructions](https://github.com/sukesh-ak/setup-mosquitto-with-docker). If the broker is not hosted on the machine where you deploy the Raspberry Pi scripts, you will need to modify the scripts by changing the IP address accordingly. Additionally, if your broker has authentication requirements, you must also incorporate them into the scripts.

To enable the dashboard functionality, you must possess a Thingboard cloud license and obtain the token for the cloud MQTT broker. You will need to update the token within the [mqtt_local_cloud_bridge](https://github.com/Federica-B/smart-dizzy-home/blob/main/raspy/mqtt_local_cloud_bridge/mqtt_local_cloud_bridge) file, specifically in the ```c_token``` variableThe token has to be changed in the file.
## Trubleshooting
If you encounter the problem of Line Feed after moving files from Windows to Unix you can use the folling command to resolve this issue:
```
dos2unix [options] [file-name]
```
If you do not possess three Arduinos, or if the Arduino models do not contain 'UNO' in their names, the bash script [start_simulation](https://github.com/Federica-B/smart-dizzy-home/blob/main/raspy/raspy_scripts/start_simulation) will not function. You can start the singular scrips manually.
