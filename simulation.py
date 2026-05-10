import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta


THINGSBOARD_HOST = '127.0.0.1' 
ACCESS_TOKEN = 'YOUR_DEVICE_ACCESS_TOKEN' # Το token της εικονικής συσκευής

def on_connect(client, userdata, flags, rc):
    print(f"Connected to IoT Platform with result code {rc}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(ACCESS_TOKEN)
# Uncomment την παρακάτω γραμμή όταν έχεις έτοιμο τον server
# client.connect(THINGSBOARD_HOST, 1883, 60)
# client.loop_start()

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
    
    
    
    
    print(f"[{event_time}] Sent -> {sensor_id}: {state} ({value} {unit})")
    time.sleep(1) # 

def scenario_1_normal_day():
    print("\n--- Starting Scenario 1: Normal Day ---")
    # 07:00 - Σηκώνεται από το κρεβάτι (Πίεση = 0)
    send_telemetry("Bed_Mat_01", "pressure", "bedroom", "unoccupied", 0, "kg", 0)
    # 07:05 - Μπαίνει μπάνιο και ανοίγει τη βρύση (Ροή νερού)
    send_telemetry("Water_Flow_Bath", "water_flow", "bathroom", "flowing", 5, "L/min", 5)
    send_telemetry("Water_Flow_Bath", "water_flow", "bathroom", "stopped", 0, "L/min", 15)
    # 07:30 - Πάει κουζίνα, ανοίγει ψυγείο και φτιάχνει καφέ
    send_telemetry("PIR_Kitchen", "motion", "kitchen", "active", 1, "boolean", 30)
    send_telemetry("Contact_Fridge", "contact", "kitchen", "open", 1, "boolean", 32)
    send_telemetry("Contact_Fridge", "contact", "kitchen", "closed", 0, "boolean", 33)
    send_telemetry("Plug_Coffee", "power", "kitchen", "on", 800, "W", 35)
    # 08:00 - Παίρνει τα φάρμακά του
    send_telemetry("Contact_Meds", "contact", "bathroom", "open", 1, "boolean", 60)
    send_telemetry("Contact_Meds", "contact", "bathroom", "closed", 0, "boolean", 61)

def scenario_2_subtle_decline():
    print("\n--- Starting Scenario 2: Subtle Decline ---")
    # 12:00 - Πάει στην κουζίνα, ανοίγει το ψυγείο αλλά ξεχνάει να το κλείσει!
    send_telemetry("Contact_Fridge", "contact", "kitchen", "open", 1, "boolean", 0)
    # Παραμένει ανοιχτό για ώρες...
    
    # 12:15 - Κάθεται στην πολυθρόνα (ανιχνεύεται δόνηση/παρουσία)
    send_telemetry("Vibration_Armchair", "vibration", "living_room", "occupied", 1, "boolean", 15)
    # 18:15 (6 ώρες μετά) - Εξακολουθεί να είναι στην πολυθρόνα (Καθιστική συμπεριφορά 6+ ωρών)
    send_telemetry("Vibration_Armchair", "vibration", "living_room", "occupied", 1, "boolean", 375)

def scenario_3_acute_hazard():
    print("\n--- Starting Scenario 3: Acute Hazard ---")
    # 19:00 - Ανάβει το μάτι της κουζίνας (Υψηλή κατανάλωση)
    send_telemetry("Plug_Stove", "power", "kitchen", "on", 2000, "W", 0)
    # 19:05 - Φεύγει από την κουζίνα και πάει στο υπνοδωμάτιο (Ανίχνευση κίνησης στο υπνοδωμάτιο)
    send_telemetry("PIR_Bedroom", "motion", "bedroom", "active", 1, "boolean", 5)
    # 19:30 - Η κουζίνα καίει ακόμα (2000W) και ο ένοικος είναι στο κρεβάτι!
    send_telemetry("Plug_Stove", "power", "kitchen", "on", 2000, "W", 30)
    send_telemetry("Bed_Mat_01", "pressure", "bedroom", "occupied", 75, "kg", 32)

# Εκτέλεση των σεναρίων
if __name__ == "__main__":
    scenario_1_normal_day()
    scenario_2_subtle_decline()
    scenario_3_acute_hazard()
    # client.loop_stop()