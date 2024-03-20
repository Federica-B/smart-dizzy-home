#!/usr/bin/env python3
import csv
import json
import random
import time
import paho.mqtt.client as mqtt

# MQTT Broker details
broker_address = "127.0.0.1"
port = 1883
topic = "data/ecg-eda"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")


def csv_to_senml(column_names, row):
    """
    Converts a CSV row to a SenML message, retaining the original column names.

    Parameters:
    - column_names: A list of column names from the CSV.
    - row: A list of values from a CSV row.

    Returns:
    - A SenML-formatted string.
    """
    # Generate a random ID
    random_id = random.randint(10000, 99999)

    # Current timestamp
    current_timestamp = time.time()

    # Initialize an empty list for SenML records
    senml_records = []

    # Skip the first and last column if they are not feature columns (e.g., ID and label)
    for name, value in zip(column_names[1:-1], row[1:-1]):
        try:
            # Attempt to convert feature value to float, if applicable
            value = float(value)
        except ValueError:
            pass  # Keep the value as-is if it can't be converted
        senml_records.append({"bn": str(random_id), "n": name, "v": value, "t": current_timestamp})

    return json.dumps(senml_records)


def read_and_send_csv(file_path, client):
    with open(file_path, 'r', newline='') as csvfile:
        ecg_reader = csv.reader(csvfile, delimiter=',')
        column_names = next(ecg_reader)
        next(ecg_reader)  # Skip the header row
        data = list(ecg_reader)

        for row in data:
            senml_message = csv_to_senml(column_names, row)
            result = client.publish(topic, senml_message)
            # result è una tupla (result_code, message_id)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                print(f"Message published successfully to {topic}")
            else:
                print(f"Failed to publish message to {topic}")
           # print(f"Sent: {senml_message}")
            time.sleep(5)


if __name__ == "__main__":
    # MQTT Client setup
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.connect(broker_address, port)

    # Replace 'path_to_your_ecg_data.csv' with the actual path to your CSV file
    csv_file_path = 'dataset/5_15_7_vb.csv'

    client.loop_start()
    read_and_send_csv(csv_file_path, client)
    client.loop_stop()
