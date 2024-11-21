import os
import subprocess
import time
import torch
import numpy as np
import cv2
import seaborn as sns
import matplotlib.pyplot as plt
from data_models import EmotionDetection
from database import PSQLManager
from PIL import Image
from facenet_pytorch import MTCNN
from transformers import AutoFeatureExtractor, AutoModelForImageClassification, AutoConfig
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

class EmotionDetector:
    def __init__(self, manager: PSQLManager ):
        if manager is not None:
            self.manager = manager
        os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        x = torch.ones(1, device=self.device)
        print("Corriendo en: {}".format(self.device))

        # Configurar MTCNN para usar CPU
        self.mtcnn = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=200,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            keep_all=False,
            device="cpu",  # Cambiar a "cpu"
        )

        self.extractor = AutoFeatureExtractor.from_pretrained("trpakov/vit-face-expression")
        self.model = AutoModelForImageClassification.from_pretrained("trpakov/vit-face-expression").to(self.device)

        self.emotions = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

    def detect_emotions(self, image):
        """
        Detectar emociones de una imagen dada.

        Returns:
        - face (PIL.Image): La cara recortada de la imagen.
        - class_probabilities (dict): Las probabilidades de cada clase de emoción.
        """
        temporary = image.copy()
        sample = self.mtcnn.detect(temporary)
        
        if sample[0] is not None:
            box = sample[0][0]
            face = temporary.crop(box)

            inputs = self.extractor(images=face, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

            config = AutoConfig.from_pretrained("trpakov/vit-face-expression")
            id2label = config.id2label

            probabilities = probabilities.cpu().numpy().tolist()[0]
            class_probabilities = {
                id2label[i]: prob for i, prob in enumerate(probabilities)
            }
            return face, class_probabilities
        return None, None

    def create_combined_image(self, face, class_probabilities):
        """
        Crear una imagen combinada con la cara detectada y un gráfico de barras con las probabilidades de emociones.
        """
        colors = {
            "angry": "red",
            "disgust": "green",
            "fear": "gray",
            "happy": "yellow",
            "neutral": "purple",
            "sad": "blue",
            "surprise": "orange",
        }
        palette = [colors[label] for label in class_probabilities.keys()]

        fig, axs = plt.subplots(1, 2, figsize=(15, 6))
        axs[0].imshow(np.array(face))
        axs[0].axis("off")

        sns.barplot(
            ax=axs[1],
            y=list(class_probabilities.keys()),
            x=[prob * 100 for prob in class_probabilities.values()],
            palette=palette,
            orient="h",
        )
        axs[1].set_xlabel("Probabilidad (%)")
        axs[1].set_title("Probabilidades de Emociones")
        axs[1].set_xlim([0, 100])

        canvas = FigureCanvas(fig)
        canvas.draw()
        img = np.frombuffer(canvas.tostring_rgb(), dtype="uint8")
        img = img.reshape(canvas.get_width_height()[::-1] + (3,))

        plt.close(fig)
        return img

    def analyze_frame(self, frame, save=False, image_output_dir=None, video_id=None, img_id=None):
        """
        Analiza un frame, detecta emociones y devuelve el frame procesado.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)

        face, class_probabilities = self.detect_emotions(pil_image)

        if face is not None:
            combined_image = self.create_combined_image(face, class_probabilities)
            combined_image_bgr = cv2.cvtColor(combined_image, cv2.COLOR_RGB2BGR)
            processed_frame = combined_image_bgr
        else:
            processed_frame = frame

        if save:
            self.save_frame(processed_frame, image_output_dir=image_output_dir)
            
            if video_id is not None:
                print("Saving video to db")
                detection = EmotionDetection(
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    img_id=img_id,
                    dominant_emotion=max(class_probabilities, key=class_probabilities.get),
                    angry_probability=round(class_probabilities["angry"], 2),
                    disgust_probability=round(class_probabilities["disgust"], 2),
                    fear_probability=round(class_probabilities["fear"], 2),
                    happy_probability=round(class_probabilities["happy"], 2),
                    neutral_probability=round(class_probabilities["neutral"], 2),
                    sad_probability=round(class_probabilities["sad"], 2),
                    surprise_probability=round(class_probabilities["surprise"], 2),
                    video_id=video_id
                )
                print(detection)
                self.manager.insert_emotion_detection(detection)

        return processed_frame

    def analyze_video(self, video_path, output_path, open_in_finder=True, save=False, frames_path=None):
        """
        Procesar video desde un archivo, detectar emociones y guardar el video procesado.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"No se pudo abrir el video {video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0.0:
            fps = 30.0

        out = None  # Inicializar el VideoWriter después
        frame_count = 0  # Contador de frames procesados
        video_id = None
        if self.manager is not None and save:
            video_id = self.manager.create_emotion_detection_video(output_path)
            
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            processed_frame = self.analyze_frame(frame, save=save, video_id=video_id, image_output_dir=frames_path)
            frame_count += 1

            if out is None:
                # Inicializar VideoWriter con el tamaño del frame procesado
                frame_height, frame_width = processed_frame.shape[:2]
                out = cv2.VideoWriter(
                    output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame_width, frame_height)
                )

            out.write(processed_frame)

            # Eliminar o comentar las siguientes líneas para no mostrar los frames
            # cv2.imshow("Detección de Emociones", processed_frame)
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break

        cap.release()
        if out is not None:
            out.release()
        # cv2.destroyAllWindows()
        print(f"Video procesado guardado en {output_path}")
        print(f"Total de frames procesados: {frame_count}")
        if open_in_finder:
            subprocess.run(["open", os.path.dirname(output_path)])

    def analyze_video_folder(self, input_folder_path, output_folder_path, number_of_videos=None, start_video=1, suffix=""):
        for i, filename in enumerate(os.listdir(input_folder_path), start=start_video):
            if number_of_videos is not None and i > number_of_videos:
                subprocess.run(["open", output_folder_path])
                print("Videos procesados")
                break
            new_video_filename = f"video{i}{suffix}.mp4"
            video_path = os.path.join(input_folder_path, filename)
            out_video_path = os.path.join(output_folder_path, new_video_filename)
            self.analyze_video(video_path, out_video_path, open_in_finder=False, save=True)
            print(f"Procesamiento completado del video {video_path}")
        subprocess.run(["open", output_folder_path])

    def analyze_photo(self, input_path, output_path):
        image = cv2.imread(input_path)
        if image is None:
            print("No se pudo cargar la imagen:", input_path)
            return
        processed_image = self.analyze_frame(image, save=True, image_output_dir=os.path.dirname(output_path))
        cv2.imwrite(output_path, processed_image)
        print(f"Imagen guardada en {output_path}")

    def analyze_photo_folder(self, folder_path, output_folder_path, number_of_images=None):
        for i, filename in enumerate(os.listdir(folder_path), start=1):
            if number_of_images is not None and i > number_of_images:
                break
            new_image_filename = f'img{i}.jpg'
            image_path = os.path.join(folder_path, filename)
            output_image_path = os.path.join(output_folder_path, new_image_filename)
            self.analyze_photo(image_path, output_image_path)
        subprocess.run(["open", output_folder_path])

    def save_frame(self, frame, image_output_dir=None):
        if image_output_dir is not None:
            if not os.path.exists(image_output_dir):
                os.makedirs(image_output_dir)
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            image_filename = f"frame_{timestamp}.jpg"
            image_path = os.path.join(image_output_dir, image_filename)
        else:
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            image_filename = f"frame_{timestamp}.jpg"
            image_path = image_filename
        cv2.imwrite(image_path, frame)
        return image_path
