import subprocess
from ultralytics import YOLO
import cv2
import os
from utils import get_center_of_bbox, measure_distance


def analyze_frame(frame, results):
    
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            confidence = box.conf[0]
            label = f"Fall: {int(confidence * 100)}%"
            start_point = (int(x1), int(y1))
            end_point = (int(x2), int(y2))
            color = (0, 255, 0)
            cv2.rectangle(frame, start_point, end_point, color, 2)
            cv2.putText(frame, label, (start_point[0], start_point[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame
    
def analyze_photo(model_path, input_path, output_path):
    model = YOLO(model_path)
    image = cv2.imread(input_path)
    results = model.predict(image, conf=0.4, iou=0.3)
    if image is None:
        print("No se pudo cargar: ", input_path)
        return
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            confidence = box.conf[0]
            label = f"Fall: {int(confidence * 100)}%"
            start_point = (int(x1), int(y1))
            end_point = (int(x2), int(y2))
            color = (0, 255, 0)
            cv2.rectangle(image, start_point, end_point, color, 2)
            cv2.putText(image, label, (start_point[0], start_point[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    print("IMWRITE: ", input_path, output_path)
    cv2.imwrite(output_path, image)
    print(f"Imagen guardada en {output_path}")
   
   
    
def analyze_frame(model_path, people_model_path, frame):
    fall_model = YOLO(model_path)
    people_model = YOLO(people_model_path)
    
    fall_results = fall_model.track(frame, conf=0.5, iou=0.3)
    people_results = people_model.track(frame, conf=0.4, iou=0.3)
    
    if frame is None:
        print("No se pudo carga: ")
        return
    
    fall_detected = False
    fall_center = None
    
    for result in fall_results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            confidence = box.conf[0]
            
            fall_center = get_center_of_bbox((x1, y1, x2, y2))
            fall_detected = True
            
            label = f"Fall: {int(confidence * 100)}%"
            start_point = (int(x1), int(y1))
            end_point = (int(x2), int(y2))
            fall_box = (int(x1), int(y1), int(x2), int(y2))
            
    for people_result in people_results:
        
        person_result_names = people_result.names
        
        for person_box in people_result.boxes:
            obj_cls_id = person_box.cls.tolist()[0]
            obj_cls_name = person_result_names[obj_cls_id]
            
            if obj_cls_name == "person":
                px1, py1, px2, py2 = person_box.xyxy[0]
                
                person_center = get_center_of_bbox((px1, py1, px2, py2))
                
                cv2.rectangle(frame, (int(px1), int(py1)), (int(px2), int(py2)), (255, 0, 0), 2)
                
                cv2.putText(frame, "Person", (int(px1), int(py1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                
                if fall_detected:
                    distance = measure_distance(fall_center, person_center)
                    if distance < 200:
                        color = (0, 255, 0)
                        cv2.rectangle(frame, start_point, end_point, color, 2)
                        cv2.putText(frame, label, (start_point[0], start_point[1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame
    
    
    
    
def analyze_photo_folder(model_path, folder_path, output_folder_path, number_of_images=None):
        for i, filename in enumerate(os.listdir(folder_path), start=1):
            if number_of_images is not None and i > number_of_images:
                break
            new_image_filename = f'img{i}.jpg'
            image_path = os.path.join(folder_path, filename)
            output_image_path = os.path.join(output_folder_path, new_image_filename)
            analyze_photo(model_path, image_path, output_image_path)
            
            subprocess.run(["open", output_folder_path])
    