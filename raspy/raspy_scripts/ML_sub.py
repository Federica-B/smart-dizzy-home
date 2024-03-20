#!/usr/bin/env python3
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
topic_stress = "data/stress"

# Upload model + scaler pretrained

clf = joblib.load('model/random_forest_model.pkl')
scaler = joblib.load('model/scaler.pkl')


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

    ## send on mqtt the prediction
    client.publish(topic_stress,prediction_label)
    print("Publish on topic: /"+ str(topic_stress)+ " value: "+ str(prediction_label))


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.connect(broker_address, port, 60)
client.on_message = on_message

client.loop_forever()
