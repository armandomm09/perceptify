import os
import subprocess
# import torch
import cv2
from ultralytics import YOLO
# from process import analyze_photo, analyze_video, analyze_photo_folder, analyze_video_folder, analyze_realtime
from constants import *
from training import continue_training, train_from_scratch
from process import analyze_video_folder, analyze_realtime, analyze_native_yolo, analyze_video
from utils import rename_and_order_files
import os



# analyze_video_folder(TRAINED_MODEL_LAST_PATH, YOLO_V_11_PATH, "media/in_videos", "media/out_videos", suffix="last")
# analyze_video_folder(TRAINED_MODEL_LAST_PATH, "media/in_videos", "media/out_videos", suffix="last")

# analyze_video(TRAINED_MODEL_LAST_PATH, YOLO_V_11_PATH, "media/in_videos/video11.mp4", "media/out_videos/video1ls.mp4")

# analyze_realtime(TRAINED_MODEL_LAST_PATH, "models/yolo11n.pt")
# analyze_native_yolo("models/face_model.h5")
# continue_training(TRAINED_MODEL_LAST_COMPLETE_PATH)
# analyze_native_yolo("models/yolo11n.pt")
# rename_and_order_files("media/in_videos", "video")