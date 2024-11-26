import asyncio
import os
from fastapi.responses import StreamingResponse, FileResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Header
import numpy as np
import cv2
from constants import TRAINED_MODEL_BEST_PATH, YOLO_V_11_PATH, DATABASE_CONFIG_PATH
from threading import Thread
import paho.mqtt.client as mqtt
from api_handlers import save_gyro_reading
from database import PSQLManager
from process import FallDetector
from emotion_detection import EmotionDetector
from utils import record_video
import uuid

latest_mqtt_value = None

conf = None
conn = None

manager = PSQLManager(DATABASE_CONFIG_PATH)

# Almacenar los frames recibidos en una lista
frame_queue = []

latest_frame = None
frame_lock = asyncio.Lock()

latest_clear_frame = None
clear_frame_lock = asyncio.Lock()

async def record_video_from_frames(output_path, duration=10, fps=10):
    global latest_clear_frame
    start_time = asyncio.get_event_loop().time()
    end_time = start_time + duration

    frames_to_write = []

    try:
        while asyncio.get_event_loop().time() < end_time:
            async with clear_frame_lock:
                if latest_clear_frame is not None:
                    print("Capturando frame:", asyncio.get_event_loop().time())
                    frame = latest_clear_frame.copy()
                    frames_to_write.append(frame)
            await asyncio.sleep(1 / fps)

        if frames_to_write:
            print(f"Frames capturados: {len(frames_to_write)}")
            height, width = frames_to_write[0].shape[:2]
            out = cv2.VideoWriter(
                output_path,
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps,
                (width, height)
            )

            for frame in frames_to_write:
                out.write(frame)

            out.release()
            print(f"Video guardado en {output_path}")
        else:
            print("No se capturaron frames para grabar el video.")
    except Exception as e:
        print(f"Ocurrió un error al grabar el video: {e}")


def create_app():
    app = FastAPI()
    client = mqtt.Client()
    client.connect('localhost', 1883)
    client.subscribe('topic')
    client.on_message = lambda client, userdata, message: save_gyro_reading(client, userdata, message, manager)
    client.loop_start()

    @app.get("/")
    async def root():
        return {"value": "latest_mqtt_value"}

    return app

app = create_app()

fall_detector = FallDetector(TRAINED_MODEL_BEST_PATH, YOLO_V_11_PATH, manager)
emotion_detector = EmotionDetector(manager)

# Variable global para controlar la detección de emociones
detect_emotion_flag = False

@app.get("/video_feed")
async def video_stream():
    async def frame_generator():
        try:
            while True:
                async with frame_lock:
                    frame = latest_frame if latest_frame is not None else default_frame
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                await asyncio.sleep(0.01)  # Pequeña pausa para ceder el control al bucle de eventos
        except asyncio.CancelledError:
            print("El cliente se ha desconectado del video feed")
        except Exception as e:
            print(f"Ocurrió una excepción en frame_generator: {e}")

    return StreamingResponse(frame_generator(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.websocket("/setvideo")
async def video_feed(websocket: WebSocket):
    global latest_frame, latest_clear_frame
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            nparr = np.frombuffer(data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is not None:
                processed_frame, fall_detected, confidence, person_count = fall_detector.analyze_frame(image, save=True)

                # Codificar la imagen procesada en JPEG
                _, buffer = cv2.imencode('.jpg', processed_frame)
                processed_data = buffer.tobytes()

                async with frame_lock:
                    latest_frame = processed_data  # Almacena la imagen procesada en bytes
                async with clear_frame_lock:
                    latest_clear_frame = image.copy()
            else:
                print("No se pudo decodificar el frame recibido")
    except WebSocketDisconnect:
        print("El cliente se desconectó")
    except Exception as e:
        print(f"Ocurrió una excepción en /setvideo: {e}")

with open("media/fall/in_images/img3.jpg", "rb") as f:
    default_frame = f.read()

@app.get("/detect_emotion")
async def detect_emotion_endpoint():
    global detect_emotion_flag
    if latest_frame is not None:
        try:
            detect_emotion_flag = True
            video_uuid = uuid.uuid4()
            # Generar un nombre único para el video
            video_filepath_in = f"media/emotions/in_videos/{video_uuid}.mp4"
            video_filepath_out = f"media/emotions/videos_runs/{video_uuid}.mp4"

            # Grabar video durante 10 segundos
            await record_video_from_frames(video_filepath_in, duration=15)

            # Procesar el video usando analyze_video
            emotion_detector.analyze_video(
                video_path=video_filepath_in,
                output_path=video_filepath_out,
                open_in_finder=False,
                save=True,
                frames_path="media/emotions/runs",
                uuid=video_uuid
            )

            detect_emotion_flag = False
            return {"video_uuid": video_uuid}
        except Exception as e:
            detect_emotion_flag = False
            print(f"Ocurrió un error en detect_emotion: {e}")
            raise HTTPException(status_code=500, detail="Error en la detección de emociones")
    else:
        return {"No stream": True}
    

@app.get("/image/{img_id}")
async def get_img(img_id: int):
    res = manager.get_img_by_id(img_id)

    if res:
        if os.path.exists(res.path):
            return FileResponse(res.path, media_type="image/jpg")
        else:
            print("File not found")
            raise HTTPException(status_code=404, detail="Image file not found")
    else:
        print("Image not found")
        raise HTTPException(status_code=404, detail="Image not found in database")


@app.get("/emotion_video/{video_id}")
async def get_video_info(video_id: str):
    video_path = f"media/emotions/videos_runs/{video_id}.mp4"
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="El archivo de video no existe")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"{video_id}.mp4",
        headers={
            "Content-Disposition": f"inline; filename={video_id}.mp4"
        }
    )
    
@app.get("/all_emotion_videos")
async def get_all_emotion_videos():
    
    videos = manager.get_all_emotion_videos()
    
    return [video.to_json() for video in videos]

@app.get("/emotions_by_video/{video_id}")
async def get_emotions_by_video(video_id: int):
    
    emotions = manager.analyze_emotions_by_video_id(video_id)
    return emotions
