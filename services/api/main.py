import os
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": 5432,
    "dbname": "solarwatch",
    "user": "postgres",
    "password": "solarwatch",
}

app = FastAPI(title="SolarWatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.get("/devices")
def list_devices():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT DISTINCT ON (device_id) device_id, type, timestamp, data
        FROM telemetry
        ORDER BY device_id, timestamp DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.get("/devices/{device_id}/history")
def device_history(device_id: str, limit: int = 50):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT device_id, type, timestamp, data
        FROM telemetry
        WHERE device_id = %s
        ORDER BY timestamp DESC
        LIMIT %s;
    """, (device_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="Device not found")
    return rows


@app.get("/alerts")
def list_alerts():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT DISTINCT ON (device_id) device_id, type, timestamp, data
        FROM telemetry
        ORDER BY device_id, timestamp DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    alerts = []
    for row in rows:
        data = row["data"]
        if row["type"] == "solar" and data.get("temperature_c", 0) > 60:
            alerts.append({
                "device_id": row["device_id"],
                "issue": "High panel temperature",
                "value": data.get("temperature_c"),
                "timestamp": row["timestamp"],
            })
        if row["type"] == "wind" and data.get("rpm", 0) > 38:
            alerts.append({
                "device_id": row["device_id"],
                "issue": "Turbine RPM too high",
                "value": data.get("rpm"),
                "timestamp": row["timestamp"],
            })
    return alerts