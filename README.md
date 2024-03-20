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


The serial communication between Arduino and Raspberry Pi is established through a USB to USB-C cable. If you decide to replicate and deploy this project, ensure that the cable you use can transmit data. Additionally, note that Arduino and Raspberry Pi operate at different voltage levels. For serial communication via GPIO pins, a 3.3V/5V level-shifter is required to safeguard the Raspberry Pi.


