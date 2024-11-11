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

from process import analyze_video
from constants import TRAINED_MODEL_LAST_PATH, YOLO_V_11_PATH, DATABASE_CONFIG_PATH
from database import PSQLManager

manager = PSQLManager(DATABASE_CONFIG_PATH)

# analyze_video(TRAINED_MODEL_LAST_PATH, YOLO_V_11_PATH, "media/in_videos/video7.mp4", "media/out_videos/video7.mp4", open_in_finder=True, save=True, manager=manager)

results = manager.get_all_cv_fall_readings()

for result in results:
    print(result)
