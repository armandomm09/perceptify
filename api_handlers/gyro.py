
from database import insert_belt_reading, load_db_config, connect_db
import json
import time
from constants import DATABASE_CONFIG_PATH
from data_models import BeltReading
from database import PSQLManager
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
            )
            
            
            latest_mqtt_value = payload
            
            manager.insert_belt_reading(reading)
            
        except json.JSONDecodeError:
            print("\rError al decodificar JSON:", payload)
    else:
        print("\rMensaje vacío recibido.", end='', flush=True)

