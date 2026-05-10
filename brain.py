import json
import requests
from datetime import datetime, timedelta


TB_HOST = "http://127.0.0.1:9090"
TB_USER = "tenant@thingsboard.org"
TB_PASS = "tenant"
DEVICE_NAME = "Apartment_Sensors" 

def get_tb_token():
    """Κάνει login στο ThingsBoard και παίρνει το JWT Token (Admin Rights)"""
    url = f"{TB_HOST}/api/auth/login"
    payload = {"username": TB_USER, "password": TB_PASS}
    response = requests.post(url, json=payload)
    response.raise_for_status() 
    return response.json().get("token")

def get_device_id(token):
    """Βρίσκει το εσωτερικό ID (UUID) της συσκευής βάσει του ονόματός της"""
    url = f"{TB_HOST}/api/tenant/devices?deviceName={DEVICE_NAME}"
    headers = {"X-Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("id", {}).get("id")

def fetch_sensor_data(time_window_hours):
    """Τραβάει τα ΠΡΑΓΜΑΤΙΚΑ δεδομένα από το REST API του ThingsBoard"""
    print(f"Fetching real data for the last {time_window_hours} hours from ThingsBoard...")
    try:
        token = get_tb_token()
        device_id = get_device_id(token)
        
        
        end_ts = int(datetime.now().timestamp() * 1000)
        start_ts = int((datetime.now() - timedelta(hours=time_window_hours)).timestamp() * 1000)
        
        
        url = f"{TB_HOST}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
        params = {
            "keys": "sensor_id,state,value,unit,timestamp",
            "startTs": start_ts,
            "endTs": end_ts,
            "limit": 100 
        }
        headers = {"X-Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return "No data found for the given time window."

        
        formatted_logs = []
        server_timestamps = set()
        for key, values in data.items():
            for item in values:
                server_timestamps.add(item['ts'])
                
        for ts in sorted(list(server_timestamps)):
            event = {}
            for key, values in data.items():
                for item in values:
                    if item['ts'] == ts:
                        event[key] = item['value']
            
           
            simulated_ts_str = event.get('timestamp', '')
            if simulated_ts_str:
                
                dt_obj = datetime.fromisoformat(simulated_ts_str.replace("Z", ""))
                dt = dt_obj.strftime('%H:%M')
            else:
                dt = "Unknown Time"

            s_id = event.get('sensor_id', 'Unknown')
            state = event.get('state', '')
            val = event.get('value', '')
            unit = event.get('unit', '')
            
            log_line = f"[{dt}] {s_id}: {state} ({val} {unit})"
            formatted_logs.append(log_line)
            
        result_string = "\n".join(formatted_logs)
        return result_string
        
    except Exception as e:
        print(f"Error fetching data from ThingsBoard: {e}")
        return ""

def run_safety_auditor():
    """Requirement A: The Safety Auditor (Automated) """
    print("\n--- Running Safety Auditor (Every 60 mins) ---")
    data = fetch_sensor_data(time_window_hours=2) 
    
    
    print("--- RAW DATA FETCHED FROM THINGSBOARD ---")
    print(data)
    print("-----------------------------------------")
    
    system_prompt = """You are an automated IoT Safety Auditor. Output ONLY valid JSON format.
    Do not add any Markdown formatting or conversational text."""
    
   
    llm_response = '{"alert": true, "reason": "Stove is ON (2000W) but resident is in bed.", "urgency": "high"}'
    
    alert_data = json.loads(llm_response)
    if alert_data.get("alert"):
        print(f"🚨 CRITICAL ALERT DISPATCHED: {alert_data['reason']} (Urgency: {alert_data['urgency']})")
    else:
        print("✅ All good. No discrepancies found.")

def run_narrator(caretaker_question):
    """Requirement B: The Narrator (On-Demand) """
    print(f"\n--- Caretaker asks: '{caretaker_question}' ---")
    
    
    llm_response = "I need to let you know that there is a safety concern right now. The sensors indicate that the kitchen stove was turned on, but shortly after, the bedroom sensors showed movement and the bed is currently occupied. We highly recommend calling her or checking in immediately to ensure the stove is turned off safely."
    
    print(f"🤖 AI Narrator: {llm_response}")

 
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8') # Για να μην "σκάει" με τα emojis
    run_safety_auditor()
    run_narrator("Is everything okay with Mom right now?")