import json
import psycopg2
import paho.mqtt.client as mqtt

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "solarwatch",
    "user": "postgres",
    "password": "solarwatch",
}


def setup_database():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id SERIAL PRIMARY KEY,
            device_id TEXT,
            type TEXT,
            timestamp TIMESTAMPTZ,
            data JSONB
        );
    """)
    conn.commit()
    return conn, cur


conn, cur = setup_database()
print("Connected to database. Waiting for telemetry...")

def on_message(client, userdata, msg):
    reading = json.loads(msg.payload.decode())
    cur.execute(
        "INSERT INTO telemetry (device_id, type, timestamp, data) VALUES (%s, %s, %s, %s)",
        (reading["device_id"], reading["type"], reading["timestamp"], json.dumps(reading)),
    )
    conn.commit()
    print(f"Saved reading from {reading['device_id']}")


client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("fleet/telemetry")
client.loop_forever()
