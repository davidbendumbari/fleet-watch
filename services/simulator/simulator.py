import json
import random
import time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
import os

BROKER = os.environ.get("MQTT_BROKER_HOST", "localhost")
PORT = 1883
NUM_SOLAR = 30
NUM_WIND = 20

client = mqtt.Client()
client.connect(BROKER, PORT, 60)


def generate_solar_reading(device_id):
    return {
        "device_id": f"solar-{device_id}",
        "type": "solar",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "voltage": round(random.uniform(280, 320), 2),
        "temperature_c": round(random.uniform(20, 65), 1),
        "output_kw": round(random.uniform(0, 5), 2),
    }


def generate_wind_reading(device_id):
    return {
        "device_id": f"wind-{device_id}",
        "type": "wind",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "rpm": round(random.uniform(10, 40), 1),
        "wind_speed_ms": round(random.uniform(2, 20), 1),
        "output_kw": round(random.uniform(0, 10), 2),
    }


print("Fleet simulator started. Publishing telemetry every 3 seconds...")
while True:
    for i in range(NUM_SOLAR):
        reading = generate_solar_reading(i)
        client.publish("fleet/telemetry", json.dumps(reading))
    for i in range(NUM_WIND):
        reading = generate_wind_reading(i)
        client.publish("fleet/telemetry", json.dumps(reading))
    print(f"Published readings for {NUM_SOLAR + NUM_WIND} devices")
    time.sleep(3)
