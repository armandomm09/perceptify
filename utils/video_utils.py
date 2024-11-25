import cv2
import time
from datetime import datetime, timedelta
import os

def record_video():
    imgs_to_save = []
    runs_dir = "/Users/armando/Progra/python/cv/fall-detection/media/fall/runs"
    actualtime = datetime.now()

    # Filtrar imágenes recientes
    images = []
    for filename in os.listdir(runs_dir):
        if filename.endswith(".jpg"):
            # Extraer timestamp del nombre del archivo
            try:
                img_timestamp = str(filename)[6:-4].split('_')[0] + str(filename)[6:-4].split('_')[1]
                file_time = datetime.strptime(img_timestamp, "%Y%m%d%H%M%S")
                time_difference = actualtime - file_time
                if time_difference < timedelta(seconds=30):  # Filtrar imágenes recientes
                    images.append((file_time, filename))
            except Exception as e:
                print(f"Error procesando archivo {filename}: {e}")

    # Ordenar imágenes por timestamp
    images.sort(key=lambda x: x[0])  # Ordena por el primer elemento (file_time)
    imgs_to_save = [img[1] for img in images]  # Extrae solo los nombres de archivo

    # Cargar imágenes para el video
    if not imgs_to_save:
        print("No hay imágenes recientes para crear el video.")
        return

    frame = cv2.imread(os.path.join(runs_dir, imgs_to_save[0]))
    height, width, layers = frame.shape

    # Nombre del archivo de video
    video_name = f"/Users/armando/Progra/python/cv/fall-detection/media/emotions/videos_runs/emotion_detection_{time.strftime('%Y%m%d_%H%M%S', time.localtime())}.mp4"

    # Crear el objeto VideoWriter
    fps = 8.38  # 9 frames por segundo
    video = cv2.VideoWriter(
        video_name,
        cv2.VideoWriter_fourcc(*'mp4v'),  # Codec H.264 para MP4
        fps,
        (width, height)
    )

    # Escribir imágenes en el video
    for img in imgs_to_save:
        video.write(cv2.imread(os.path.join(runs_dir, img)))

    cv2.destroyAllWindows()
    video.release()
    print(f"Video creado exitosamente: {video_name}")

