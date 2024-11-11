import subprocess
import time
import cv2
from ultralytics import YOLO
import os
from database import PSQLManager
from data_models import FallCameraReading

class FallDetector:
    def __init__(self, fall_model_path, person_model_path, manager: PSQLManager):
        self.fall_model = YOLO(fall_model_path)
        self.person_model = YOLO(person_model_path)
        self.manager = manager

    @staticmethod
    def get_center_of_bbox(box):
        x1, y1, x2, y2 = box
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        return (center_x, center_y)

    @staticmethod
    def measure_distance(p1, p2):
        return ((p1[0] - p2[0]) **2 + (p1[1] - p2[1]) **2) ** 0.5

    def save_frame(self, frame, image_output_dir="/Users/armando/Progra/python/cv/fall-detection/media/runs"):
        if image_output_dir is not None:
            if not os.path.exists(image_output_dir):
                os.makedirs(image_output_dir)
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            image_filename = f"frame_{timestamp}.jpg"
            image_path = os.path.join(image_output_dir, image_filename)
        else:
            # Si no se especifica image_output_dir, guardar en el directorio actual
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            image_filename = f"frame_{timestamp}.jpg"
            image_path = image_filename
        # Guardar la imagen
        cv2.imwrite(image_path, frame)
        return image_path

    def analyze_frame(self, frame, save=False, image_output_dir=None):
        fall_results = self.fall_model.track(frame, conf=0.5, iou=0.3)
        person_results = self.person_model.track(frame, conf=0.4, iou=0.3)

        fall_detected = False
        fall_center = None
        confidence = 0
        person_count = 0
        start_point = None
        end_point = None

        for result in fall_results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                confidence = box.conf[0]
                label = f"Fall: {int(confidence * 100)}%"
                start_point = (int(x1), int(y1))
                end_point = (int(x2), int(y2))
                fall_center = self.get_center_of_bbox((x1, y1, x2, y2))
                fall_detected = True
                break
            if fall_detected:
                break

        for person_result in person_results:
            person_names = person_result.names
            for person_box in person_result.boxes:
                obj_cls_id = person_box.cls.tolist()[0]
                obj_cls_name = person_names[obj_cls_id]
                if obj_cls_name == "person":
                    person_count += 1
                    px1, py1, px2, py2 = person_box.xyxy[0]
                    person_center = self.get_center_of_bbox((px1, py1, px2, py2))
                    cv2.rectangle(frame, (int(px1), int(py1)), (int(px2), int(py2)), (255, 0, 0), 2)
                    cv2.putText(frame, "Person", (int(px1), int(py1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    if fall_detected:
                        distance = self.measure_distance(fall_center, person_center)
                        if distance < 200:
                            color = (0, 255, 0)
                            cv2.rectangle(frame, start_point, end_point, color, 2)
                            cv2.putText(frame, label, (start_point[0], start_point[1] - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        # Guardar datos y llamar a save_frame
        if save:
            # Crear instancia de FallCameraReading
            # Insertar datos en la base de datos
            path = self.save_frame(frame)
            
            if self.manager is not None:
                img_id = self.manager.insert_image(path)
                data = FallCameraReading(
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    fall_detected=fall_detected,
                    confidence=int(confidence * 100),
                    num_people_detected=person_count,
                    image_id=img_id
                )
                print(img_id)
                self.manager.insert_cv_reading(data)
            # Llamar a la función save_frame para guardar el frame

        return frame, fall_detected, confidence, person_count

    def analyze_video(self, video_path, output_path, open_in_finder=True, save=False):
        cap = cv2.VideoCapture(video_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        out = cv2.VideoWriter(
            output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame_width, frame_height)
        )

        # Definir directorio para guardar imágenes
        image_output_dir = os.path.join(os.path.dirname(output_path), "frames")
        if save and not os.path.exists(image_output_dir):
            os.makedirs(image_output_dir)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            processed_frame, fall_detected, confidence, person_count = self.analyze_frame(
                frame, save=save
            )
            out.write(processed_frame)
        cap.release()
        out.release()
        print(f"Processed video saved at {output_path}")
        if open_in_finder:
            subprocess.run(["open", os.path.dirname(output_path)])

    def analyze_video_folder(self, input_folder_path, output_folder_path, number_of_videos=None, start_video=1, suffix=""):
        for i, filename in enumerate(os.listdir(input_folder_path), start=start_video):
            if number_of_videos is not None and i > number_of_videos:
                subprocess.run(["open", output_folder_path])
                print("Videos processed")
                break
            new_video_filename = f"video{i}{suffix}.mp4"
            video_path = os.path.join(input_folder_path, filename)
            out_video_path = os.path.join(output_folder_path, new_video_filename)
            self.analyze_video(video_path, out_video_path, open_in_finder=False, save=True)
            print(f"Finished processing video {video_path}")
        subprocess.run(["open", output_folder_path])

    def analyze_photo(self, input_path, output_path):
        image = cv2.imread(input_path)
        if image is None:
            print("Could not load image:", input_path)
            return
        processed_image, _, _, _ = self.analyze_frame(image, save=True, image_output_dir=os.path.dirname(output_path))
        cv2.imwrite(output_path, processed_image)
        print(f"Image saved at {output_path}")

    def analyze_photo_folder(self, folder_path, output_folder_path, number_of_images=None):
        for i, filename in enumerate(os.listdir(folder_path), start=1):
            if number_of_images is not None and i > number_of_images:
                break
            new_image_filename = f'img{i}.jpg'
            image_path = os.path.join(folder_path, filename)
            output_image_path = os.path.join(output_folder_path, new_image_filename)
            self.analyze_photo(image_path, output_image_path)
        subprocess.run(["open", output_folder_path])
