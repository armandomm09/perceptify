
from database import insert_belt_reading, load_db_config, connect_db
import json
import time
from constants import DATABASE_CONFIG_PATH


def save_gyro_reading(client, userdata, message):
    global latest_mqtt_value
    payload = message.payload.decode('utf-8')  # Decodifica el mensaje a texto
    
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # Formato: "YYYY-MM-DD HH:MM:SS"
    
    if payload:
        try:
            
            payload = json.loads(payload)
            
            gyro_x = payload.get('gyro_x', None)
            gyro_y = payload.get('gyro_y', None)
            gyro_z = payload.get('gyro_z', None)
            accel_x = payload.get('accel_x', None)
            accel_y = payload.get('accel_y', None)
            accel_z = payload.get('accel_z', None)
            
            
            latest_mqtt_value = payload
            
            conf = load_db_config(DATABASE_CONFIG_PATH)
            conn = connect_db(conf)
            insert_belt_reading(conn, timestamp, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z)
            
            print(f"\r[{timestamp}] gyro_x: {gyro_x}, gyro_y: {gyro_y}, gyro_z: {gyro_z} | accel_x: {accel_x}, accel_y: {accel_y}, accel_z: {accel_z}", end='', flush=True)
        except json.JSONDecodeError:
            print("\rError al decodificar JSON:", payload)
    else:
        print("\rMensaje vacío recibido.", end='', flush=True)

