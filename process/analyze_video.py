import subprocess
import cv2
from ultralytics import YOLO
import os


def get_center_of_bbox(box):
    x1, y1, x2, y2 = box
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)
    return (center_x, center_y)


def measure_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def analyze_video(
    fall_model_path, person_model_path, video_path, output_path, open_in_finder=True
):
    fall_model = YOLO(fall_model_path)
    person_model = YOLO(person_model_path)

    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    out = cv2.VideoWriter(
        output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame_width, frame_height)
    )

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        fall_results = fall_model.track(frame, conf=0.5, iou=0.3)
        person_results = person_model.track(frame, conf=0.5, iou=0.3)

        fall_detected = False
        fall_center = None

        for result in fall_results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                confidence = box.conf[0]

                fall_center = get_center_of_bbox((x1, y1, x2, y2))
                fall_detected = True
                label = f"Fall: {int(confidence * 100)}%"
                fall_box = (int(x1), int(y1), int(x2), int(y2))

        for person_result in person_results:

            person_result_names = person_result.names

            for person_box in person_result.boxes:
                obj_cls_id = person_box.cls.tolist()[0]
                obj_cls_name = person_result_names[obj_cls_id]

                if obj_cls_name == "person":
                    px1, py1, px2, py2 = person_box.xyxy[0]

                    person_center = get_center_of_bbox((px1, py1, px2, py2))

                    cv2.rectangle(
                        frame,
                        (int(px1), int(py1)),
                        (int(px2), int(py2)),
                        (255, 0, 0),
                        2,
                    )
                    cv2.putText(
                        frame,
                        "Person",
                        (int(px1), int(py1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        2,
                    )

                    if fall_detected:
                        distance = measure_distance(fall_center, person_center)
                        if distance < 200:
                            color = (0, 255, 0)

                            cv2.rectangle(frame, fall_box[:2], fall_box[2:], color, 2)
                            cv2.putText(
                                frame,
                                label,
                                (fall_box[0], fall_box[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                color,
                                2,
                            )

                        break
                else:
                    break

        out.write(frame)

    cap.release()
    out.release()
    print(f"Video procesado guardado en {output_path}")
    if open_in_finder:
        subprocess.run(["open", os.path.dirname(output_path)])


def analyze_video_folder(
    model_path,
    person_model_path,
    input_folder_path,
    output_folder_path,
    number_of_videos=None,
    start_video=1,
    suffix="",
):
    for i, filename in enumerate(os.listdir(input_folder_path), start=start_video):
        if number_of_videos is not None and i > number_of_videos:
            subprocess.run(["open", output_folder_path])
            print("Videos processed")
            break
        new_video_filename = f"video{i}{suffix}.mp4"
        video_path = os.path.join(input_folder_path, filename)
        out_video_path = os.path.join(output_folder_path, new_video_filename)
        analyze_video(model_path, person_model_path, video_path, out_video_path, False)
        print("Finished processing videos")

    subprocess.run(["open", output_folder_path])
