from ultralytics import YOLO
import cv2
import torch
import math

def analyze_native_yolo(model_path):
    
    # start webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    # model
    model = YOLO(model_path)

    # object classes
    classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
                "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
                "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                "teddy bear", "hair drier", "toothbrush"
                ]


    while True:
        success, img = cap.read()
        results = model.track(img, stream=True)

        # coordinates
        for r in results:
            boxes = r.boxes

            for box in boxes:
                # bounding box
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

                # put box in cam
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                # confidence
                confidence = math.ceil((box.conf[0]*100))/100
                print("Confidence --->",confidence)

                # class name
                cls = int(box.cls[0])
                # print("Class name -->", classNames[cls])

                # object details
                org = [x1, y1]
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                color = (255, 0, 0)
                thickness = 2

                cv2.putText(img, "emotion", org, font, fontScale, color, thickness)

        cv2.imshow('Webcam', img)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
def get_center_of_bbox(box):
    x1, y1, x2, y2 = box
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)
    return (center_x, center_y)

def measure_distance(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

def analyze_realtime(fall_model_path, person_model_path, label="Fall"):
    fall_model = YOLO(fall_model_path)
    person_model = YOLO(person_model_path)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo obtener el fotograma de la cámara.")
            break

        fall_results = fall_model.predict(frame, conf=0.5, iou=0.3)
        person_results = person_model.predict(frame, conf=0.5, iou=0.3)

        fall_detected = False
        fall_center = None
        fall_box = None

        # Procesar resultados de detección de caídas
        for result in fall_results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                confidence = box.conf[0]

                fall_center = get_center_of_bbox((x1, y1, x2, y2))
                fall_detected = True
                label = f"Fall: {int(confidence * 100)}%"
                fall_box = (int(x1), int(y1), int(x2), int(y2))

        # Procesar resultados de detección de personas
        for person_result in person_results:
            person_result_names = person_result.names

            for person_box in person_result.boxes:
                obj_cls_id = int(person_box.cls[0])
                obj_cls_name = person_result_names[obj_cls_id]

                if obj_cls_name == "person":
                    px1, py1, px2, py2 = person_box.xyxy[0]
                    person_center = get_center_of_bbox((px1, py1, px2, py2))

                    # Dibujar rectángulo alrededor de la persona
                    cv2.rectangle(frame, (int(px1), int(py1)), (int(px2), int(py2)), (255, 0, 0), 2)
                    cv2.putText(frame, "Person", (int(px1), int(py1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    if fall_detected:
                        distance = measure_distance(fall_center, person_center)
                        if distance < 200:
                            color = (0, 255, 0)
                            # Dibujar rectángulo alrededor de la caída
                            cv2.rectangle(frame, fall_box[:2], fall_box[2:], color, 2)
                            cv2.putText(frame, label, (fall_box[0], fall_box[1] - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    break  # Solo procesar la primera persona detectada

        # Mostrar el fotograma procesado
        cv2.imshow("Fall Detection - Realtime", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
