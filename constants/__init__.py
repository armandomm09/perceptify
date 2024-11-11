import os
import dotenv

dotenv.load_dotenv()

TRAINED_MODEL_LAST_PATH = "runs/detect/train9/weights/last.pt"
TRAINED_MODEL_LAST_COMPLETE_PATH = "/Users/armando/Progra/python/cv/fall-detection/runs/detect/train9/weights/last.pt"

TRAINED_MODEL_BEST_PATH = "runs/detect/train9/weights/best.pt"
TRAINED_MODEL_BEST_PATH = "/Users/armando/Progra/python/cv/fall-detection/runs/detect/train9/weights/best.pt"

YOLO_V_11_PATH = "models/yolo11n.pt"

DATASET_PATH = "/Users/armando/Progra/python/cv/fall-detection/Fall-Detection-4"

INPUT_IMAGES_FOLDER_PATH = "media/in_images"
INPUT_VIDEOS_FOLDER_PATH = "media/in_videos"

OUTPUT_IMAGES_FOLDER_PATH = "media/out_images"
OUTPUT_VIDEOS_FOLDER_PATH = "media/out_videos"

DATABASE_CONFIG_PATH = "database/database.ini"

XIME_CHAT_ID = os.getenv("XIME_WHATSAPP_ID")
IOT_GROUP_ID = os.getenv("IOT_GROUP_ID")