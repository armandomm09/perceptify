from whatsapp import notify_fall_detection
import json
import time
from constants import DATABASE_CONFIG_PATH, XIME_CHAT_ID, IOT_GROUP_ID
from data_models import BeltReading
from database import PSQLManager
import os
import dotenv

dotenv.load_dotenv()
def save_gyro_reading(client, userdata, message, manager: PSQLManager):
    global latest_mqtt_value
    payload = message.payload.decode('utf-8')  
    
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  
    
    if payload:
        try:
            
            payload = json.loads(payload)
            
            reading = BeltReading(
                timestamp=timestamp,
                gyro_x = payload.get('gyro_x', None),
                gyro_y = payload.get('gyro_y', None),
                gyro_z = payload.get('gyro_z', None),
                accel_x = payload.get('accel_x', None),
                accel_y = payload.get('accel_y', None),
                accel_z = payload.get('accel_z', None),
                fall = payload.get('fall', None)
            )
            print(reading.fall)
            print(reading)
            
            
            if reading.fall == 1:
                last_img = manager.get_last_fall_detected_img()
                print(last_img.id)
                alert = manager.get_cv_reading_from_img_id(last_img.id).alert(timestamp=reading.timestamp)
                print(alert)
                notify_fall_detection(XIME_CHAT_ID, alert, False, int(last_img.id))
            
            latest_mqtt_value = payload
            
            manager.insert_belt_reading(reading)
            
        except json.JSONDecodeError:
            print("\rError al decodificar JSON:", payload)
    else:
        print("\rMensaje vacío recibido.", end='', flush=True)

