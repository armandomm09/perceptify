import cv2
import asyncio
import websockets
import numpy as np

async def send_video_stream():
    
    uri = "ws://localhost:8000/setvideo"

    
    async with websockets.connect(uri) as websocket:
        
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()

            
            await websocket.send(frame_data)
            print("Frame enviado")

            
            await asyncio.sleep(0.1)  

        cap.release()


asyncio.get_event_loop().run_until_complete(send_video_stream())
