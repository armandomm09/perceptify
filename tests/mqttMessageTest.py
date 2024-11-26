# import cv2
# import asyncio
# import websockets
# import numpy as np

# async def send_video_stream():
    
#     uri = "ws://localhost:8000/setvideo"

    
#     async with websockets.connect(uri) as websocket:
        
#         cap = cv2.VideoCapture(0)

#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break

            
#             _, buffer = cv2.imencode('.jpg', frame)
#             frame_data = buffer.tobytes()

            
#             await websocket.send(frame_data)
#             print("Frame enviado")

            
#             await asyncio.sleep(0.1)  

#         cap.release()


# asyncio.get_event_loop().run_until_complete(send_video_stream())

# from database import PSQLManager 

# manager = PSQLManager("database/database.ini")

# readings = manager.get_all_belt_readings()

# print(readings[0])

# from process import analyze_video
# from constants import TRAINED_MODEL_LAST_PATH, YOLO_V_11_PATH, DATABASE_CONFIG_PATH
# from database import PSQLManager

# manager = PSQLManager(DATABASE_CONFIG_PATH)

# # analyze_video(TRAINED_MODEL_LAST_PATH, YOLO_V_11_PATH, "media/in_videos/video7.mp4", "media/out_videos/video7.mp4", open_in_finder=True, save=True, manager=manager)

# results = manager.get_all_cv_fall_readings()

# for result in results:
#     print(result)


import paho.mqtt.client as mqtt
import json
import time

# Configura los detalles del broker MQTT
broker = "localhost"  # Cambia si usas otra IP o dominio
port = 1883          # Puerto del broker MQTT (puedes ajustarlo si usas otro)
topic = "topic"       # Cambia al tema que usas en tu ESP

# Crear un mensaje de ejemplo similar al que envía la ESP
def create_sample_message():
    message = {
        "gyro_x": 1.23,
        "gyro_y": 2.34,
        "gyro_z": 3.45,
        "accel_x": 4.56,
        "accel_y": 5.67,
        "accel_z": 6.78,
        "fall": 1.0  # Ajusta a 1.0 para verdadero o 0.0 para falso si simulas un booleano
    }
    return json.dumps(message)  # Convierte el diccionario en formato JSON

# Función para publicar el mensaje de muestra en el broker MQTT
def publish_sample_message():
    client = mqtt.Client()

    try:
        client.connect(broker, port, 60)
        sample_message = create_sample_message()
        client.publish(topic, sample_message)
        print(f"Mensaje enviado: {sample_message}")
    except Exception as e:
        print(f"Error al conectar o enviar el mensaje: {e}")
    finally:
        client.disconnect()

# Ejecuta la publicación de ejemplo
if __name__ == "__main__":
    publish_sample_message()
