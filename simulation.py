import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta

THINGSBOARD_HOST = '127.0.0.1' 

ACCESS_TOKEN = 'Z3KW0HFxEMHIT3e3eWn2' 

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected to IoT Platform with result code {rc}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(ACCESS_TOKEN)


client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

def send_telemetry(sensor_id, sensor_type, location, state, value, unit, time_offset_minutes):
    """Δημιουργεί το JSON schema και το στέλνει μέσω MQTT"""
    
    event_time = (datetime.now() + timedelta(minutes=time_offset_minutes)).isoformat() + "Z"
    
    payload = {
        "timestamp": event_time,
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "location": location,
        "state": state,
        "value": value,
        "unit": unit,
        "battery_level": 95
    }
    
    
    client.publish('v1/devices/me/telemetry', json.dumps(payload), 1)
    
    print(f"[{event_time}] Sent -> {sensor_id}: {state} ({value} {unit})")
    time.sleep(1) 

def scenario_1_normal_day():
    print("\n--- Starting Scenario 1: Normal Day ---")
    send_telemetry("Bed_Mat_01", "pressure", "bedroom", "unoccupied", 0, "kg", 0)
    send_telemetry("Water_Flow_Bath", "water_flow", "bathroom", "flowing", 5, "L/min", 5)
    send_telemetry("Water_Flow_Bath", "water_flow", "bathroom", "stopped", 0, "L/min", 15)
    send_telemetry("PIR_Kitchen", "motion", "kitchen", "active", 1, "boolean", 30)
    send_telemetry("Contact_Fridge", "contact", "kitchen", "open", 1, "boolean", 32)
    send_telemetry("Contact_Fridge", "contact", "kitchen", "closed", 0, "boolean", 33)
    send_telemetry("Plug_Coffee", "power", "kitchen", "on", 800, "W", 35)
    send_telemetry("Contact_Meds", "contact", "bathroom", "open", 1, "boolean", 60)
    send_telemetry("Contact_Meds", "contact", "bathroom", "closed", 0, "boolean", 61)

def scenario_2_subtle_decline():
    print("\n--- Starting Scenario 2: Subtle Decline ---")
    send_telemetry("Contact_Fridge", "contact", "kitchen", "open", 1, "boolean", 0)
    send_telemetry("Vibration_Armchair", "vibration", "living_room", "occupied", 1, "boolean", 15)
    send_telemetry("Vibration_Armchair", "vibration", "living_room", "occupied", 1, "boolean", 375)

def scenario_3_acute_hazard():
    print("\n--- Starting Scenario 3: Acute Hazard ---")
    send_telemetry("Plug_Stove", "power", "kitchen", "on", 2000, "W", 0)
    send_telemetry("PIR_Bedroom", "motion", "bedroom", "active", 1, "boolean", 5)
    send_telemetry("Plug_Stove", "power", "kitchen", "on", 2000, "W", 30)
    send_telemetry("Bed_Mat_01", "pressure", "bedroom", "occupied", 75, "kg", 32)


if __name__ == "__main__":
    scenario_1_normal_day()
    scenario_2_subtle_decline()
    scenario_3_acute_hazard()
    
   
    time.sleep(2) 
    client.loop_stop()