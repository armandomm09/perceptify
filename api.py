import asyncio
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import numpy as np
import cv2
from process import analyze_frame
from constants import TRAINED_MODEL_BEST_PATH, YOLO_V_11_PATH, DATABASE_CONFIG_PATH
from threading import Thread
import paho.mqtt.client as mqtt
from api_handlers import save_gyro_reading
from database import PSQLManager

latest_mqtt_value = None

conf = None
conn = None

manager = PSQLManager(DATABASE_CONFIG_PATH)

def create_app():
    app = FastAPI()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect('localhost', 1883)  
    client.subscribe('topic')
    client.on_message = lambda client, userdata, message: save_gyro_reading(client, userdata, message, manager) 
    client.loop_start()
    
    

    @app.get("/")
    async def root():
        return {"value": "latest_mqtt_value"}

    return app

app = create_app()



latest_frame = None
frame_lock = asyncio.Lock()


@app.websocket("/setvideo")
async def video_feed(websocket: WebSocket):
    global latest_frame
    await websocket.accept()
    try:
        while True:
            
            data = await websocket.receive_bytes()
            # print("Recibido un frame de video")
            
            nparr = np.frombuffer(data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is not None:
                
                processed_image = analyze_frame(TRAINED_MODEL_BEST_PATH, "yolov5nu.pt", image, save=True)
                
                _, buffer = cv2.imencode('.jpg', processed_image)
                processed_data = buffer.tobytes()
                
                async with frame_lock:
                    latest_frame = processed_data
            else:
                print("No se pudo decodificar el frame recibido")
    except WebSocketDisconnect:
        print("El cliente se desconectó")

with open("media/in_images/img3.jpg", "rb") as f:
    default_frame = f.read()
    
@app.get("/video_feed")
async def video_stream():
    async def frame_generator():
        while True:
            
            frame = latest_frame if latest_frame is not None else default_frame    
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    return StreamingResponse(frame_generator(), media_type='multipart/x-mixed-replace; boundary=frame')
