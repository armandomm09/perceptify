import asyncio
import os
from fastapi.responses import StreamingResponse, FileResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
import numpy as np
import cv2
from constants import TRAINED_MODEL_BEST_PATH, YOLO_V_11_PATH, DATABASE_CONFIG_PATH
from threading import Thread
import paho.mqtt.client as mqtt
from api_handlers import save_gyro_reading
from database import PSQLManager
from process import FallDetector
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

detector = FallDetector(TRAINED_MODEL_BEST_PATH, YOLO_V_11_PATH, manager)


@app.websocket("/setvideo")
async def video_feed(websocket: WebSocket):
    global latest_frame
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            
            nparr = np.frombuffer(data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is not None:
                processed_frame, fall_detected, confidence, person_count = detector.analyze_frame(image)
                
                _, buffer = cv2.imencode('.jpg', processed_frame)
                processed_data = buffer.tobytes()
                
                async with frame_lock:
                    latest_frame = processed_data
                
                await websocket.send_bytes(processed_data)
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
            async with frame_lock:
                frame = latest_frame if latest_frame is not None else default_frame    
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    return StreamingResponse(frame_generator(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/image/{img_id}")
async def get_img(img_id: int):
    res = manager.get_img_by_id(img_id)
    
    if res:
        print(res.path)
        if os.path.exists(res.path):
            return FileResponse(res.path, media_type="image/jpg")
        else:
            print("file not found")
            raise HTTPException(status_code=404, detail="Image file not found")
    else:
        print("image not found")
        raise HTTPException(status_code=404, detail="Image not found in database")
        
    