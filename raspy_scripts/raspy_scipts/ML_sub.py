import paho.mqtt.client as mqtt
import json
import joblib
import numpy as np
import serial
import time

# Setup MQTT broker
broker_address = "127.0.0.1"
port = 1883
topic = "data/ecg-eda"

# Setup Arduino port
arduino_serial = serial.Serial('/dev/ttyACM0', 9600)  # Su Linux/Mac
# arduino_port = "COM3"  # Su Windows

# Upload model + scaler pretrained
# TODO: change path
clf = joblib.load('/Users/olivia1/Desktop/ING/1° ANNO/1° SEM/IOT/Iot_project/model/random_forest_model.pkl')
scaler = joblib.load('/Users/olivia1/Desktop/ING/1° ANNO/1° SEM/IOT/Iot_project/model/scaler.pkl')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)


# Senml_to_features function
def senml_to_features(senml_string):
    """
    Converts a SenML-formatted string back into a list of feature values.

    Parameters:
    - senml_string (str): The SenML data in JSON format.

    Returns:
    - A list of feature values extracted from the SenML records.
    """
    try:
        # Parse the SenML JSON string into a Python list
        senml_data = json.loads(senml_string)

        # Extract the 'v' (value) from each record and store it in a list
        feature_values = [record['v'] for record in senml_data]

        return feature_values
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

################# FUNZIONE PER MENDARE A SERIALE ####################
def send_data(data):
    """
    Invia i dati alla porta seriale per Arduino.
    """
    arduino_serial.write(data.encode())  # Invia il dato come stringa codificata in bytes
    time.sleep(0.1)


def on_message(client, userdata, msg):
    print("Messaggio ricevuto")
    senml_string = msg.payload.decode()

    # Convert SenML to features, excluding timestamps
    features_array = senml_to_features(senml_string)

    # Reshape the array for prediction (assuming clf is your trained model and scaler is your StandardScaler instance)
    features_np_array = np.array(features_array).reshape(1, -1)
    features_scaled = scaler.transform(features_np_array)

    # Make a prediction
    prediction = clf.predict(features_scaled)
    prediction_label = '1' if prediction[0] == 1 else '0'
    print(f"Prediction: {prediction_label}")

    # INVIO DATI A SERIALE --> teoricamente si può fare con pin out e ricezione invece sensing della temperatura con seriale
    send_data(prediction_label)


client = mqtt.Client()
client.on_connect = on_connect
client.connect(broker_address, port, 60)
client.on_message = on_message

client.loop_forever()
