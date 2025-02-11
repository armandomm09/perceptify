from whatsapp import notify_fall_detection
import json
import time
from constants import DATABASE_CONFIG_PATH, XIME_CHAT_ID, IOT_GROUP_ID
from data_models import BeltReading
from database import PSQLManager
import os
import dotenv
import datetime

dotenv.load_dotenv()


last_alert_time = None

def save_gyro_reading(client, userdata, message, manager: PSQLManager):
    global last_alert_time
    payload = message.payload.decode('utf-8')  
    timestamp = datetime.datetime.now()

    if payload:
        try:
            payload = json.loads(payload)
            fall_value = payload.get('fall', 0)
            fall_value = int(fall_value) if fall_value is not None else 0

            reading = BeltReading(
                timestamp=timestamp,
                gyro_x=payload.get('gyro_x', None),
                gyro_y=payload.get('gyro_y', None),
                gyro_z=payload.get('gyro_z', None),
                accel_x=payload.get('accel_x', None),
                accel_y=payload.get('accel_y', None),
                accel_z=payload.get('accel_z', None),
                fall=fall_value
            )

            if reading.fall == 1:

                last_minute_time = datetime.datetime.now() - datetime.timedelta(minutes=0.25)
                
                if last_alert_time is None or (timestamp - last_alert_time).total_seconds() > 30:
                    print("No se ha enviado una alerta en el último minuto, enviando alerta con imagen.")
                    
                    last_img = manager.get_last_fall_detected_img()
                    if last_img:
                        alert = f"Detección de caída a las {timestamp}."
                        
                        notify_fall_detection(XIME_CHAT_ID, alert, False, int(last_img.id))
                        
                        last_alert_time = timestamp
                    else:
                        print("No se encontró una imagen de caída reciente para adjuntar en la alerta.")
                else:
                    print("Alerta enviada en el último minuto, suprimiendo alerta duplicada.")
            
            manager.insert_belt_reading(reading)
            previous_fall_status = reading.fall

        except json.JSONDecodeError:
            print("\rError al decodificar JSON:", payload)
    else:
        print("\rMensaje vacío recibido.", end='', flush=True)
