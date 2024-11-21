import os
import subprocess
import cv2
from ultralytics import YOLO
from constants import *
from training import continue_training, train_from_scratch
from utils import rename_and_order_files
import os
from process import FallDetector
from database import PSQLManager
from emotion_detection import EmotionDetector

manager = PSQLManager(DATABASE_CONFIG_PATH)
detector = EmotionDetector(manager)
detector.analyze_video("media/emotions/in_videos/video_heri.mp4", "media/emotions/out_videos/video_heri.mp4", open_in_finder=True, save=True, frames_path="media/emotions/runs")
# detector.analyze_photo("media/emotions/in_images/IMG_4685.JPG", "media/emotions/out_images/IMG_4685.JPG")
# detector = FallDetector(TRAINED_MODEL_BEST_PATH, YOLO_V_11_PATH, manager)
# detector.analyze_video("media/in_videos/video7.mp4", "media/out_videos/video7.mp4", save=True, open_in_finder=True)

# results = manager.get_all_cv_fall_readings()
# imgs = manager.get_all_images()

# print(results[0])
# print(imgs[0])