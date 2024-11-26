from configparser import ConfigParser
import psycopg2
from data_models import BeltReading, FallCameraReading, DetectionImage, EmotionDetection, EmotionDetectionVideo


class PSQLManager:

    def __init__(self, config_file, section="postgresql"):
        parser = ConfigParser()
        parser.read(config_file)

        config = {}

        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                config[param[0]] = param[1]
        else:
            raise Exception(
                "Section {0} not found in the {1} file".format(section, config_file)
            )

        self.conf = config
        self.conn = self.connect_db(self.conf)

    def connect_db(self, conf):

        try:
            with psycopg2.connect(**conf) as conn:
                return conn
        except (psycopg2.DatabaseError, Exception) as e:
            raise Exception("Could not connect to database")
        
    def get_cv_falls_since(self, since_timestamp):
        try:
            cursor = self.conn.cursor()
            print(f"Fetching CV falls since {since_timestamp}")
            query = """
                SELECT * FROM fall_detection
                WHERE fall_detected = true AND timestamp >= %s
                ORDER BY timestamp DESC
            """
            cursor.execute(query, (since_timestamp,))
            rows = cursor.fetchall()
            print(f"Number of CV falls found: {len(rows)}")
            readings = [
                FallCameraReading(
                    id=row[0],
                    timestamp=row[1],
                    fall_detected=row[2],
                    confidence=row[3],
                    num_people_detected=row[4],
                    img_id=row[5]
                )
                for row in rows
            ]
            return readings > 0
        except Exception as e:
            print("Error fetching CV falls since timestamp: ", e)
            return False
        
    def get_belt_fall_detections_since(self, timestamp):
        try:
            cursor = self.conn.cursor()
            
            query = """
                SELECT * FROM belt_reading
                WHERE fall = true AND timestamp >= %s
                ORDER BY timestamp DESC
            """
            cursor.execute(query, timestamp)
            rows = cursor.fetchall()
         
            readings = [
            BeltReading(
                id=row[0],
                timestamp=row[1],
                gyro_x=row[2],
                gyro_y=row[3],
                gyro_z=row[4],
                accel_x=row[5],
                accel_y=row[6],
                accel_z=row[7],
                fall=row[8],
            )
            for row in rows
            ]
            return readings > 0
        except Exception as e:
            print(f"Error fetching belt readings since {timestamp}: {e}")
            return False


    def get_all_belt_readings(self):
        cur = self.conn.cursor()

        cur.execute("SELECT * FROM belt_reading")

        rows = cur.fetchall()

        readings = [
            BeltReading(
                id=row[0],
                timestamp=row[1],
                gyro_x=row[2],
                gyro_y=row[3],
                gyro_z=row[4],
                accel_x=row[5],
                accel_y=row[6],
                accel_z=row[7],
                fall=row[8],
            )
            for row in rows
        ]

        return readings

    def insert_belt_reading(self, reading: BeltReading):
        try:
            cursor = self.conn.cursor()
            print(reading)
            query = """
            INSERT INTO belt_reading (timestamp, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z, fall)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    reading.timestamp,
                    reading.gyro_x,
                    reading.gyro_y,
                    reading.gyro_z,
                    reading.accel_x,
                    reading.accel_y,
                    reading.accel_z,
                    bool(reading.fall),
                ),
            )
            self.conn.commit()
            cursor.close()
        except Exception as e:
            self.conn.rollback()
            print(f"Error al insertar datos en belt_reading: {e}")

    def get_all_cv_fall_readings(self):

        cur = self.conn.cursor()

        cur.execute("SELECT * FROM fall_detection")

        rows = cur.fetchall()

        readings = [
            FallCameraReading(
                id=row[0],
                timestamp=row[1],
                fall_detected=row[2],
                confidence=row[3],
                num_people_detected=row[4],
            )
            for row in rows
        ]
        return readings

    def insert_fall_detection(self, reading: FallCameraReading):
        try:
            cursor = self.conn.cursor()

            query = """
            INSERT INTO fall_detection (timestamp, fall_detected, confidence, num_people_detected, img_id)
            VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    reading.timestamp,
                    reading.fall_detected,
                    reading.confidence,
                    reading.num_people_detected,
                    reading.img_id,
                ),
            )

            self.conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al insertar datos en fall_detection: {e}")

    def insert_image(self, file_path):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO images (path) VALUES (%s) RETURNING id", (file_path,)
            )
            img_id = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return img_id
        except Exception as e:
            print("Error al insertar la imagen en la base de datos: ", e)

    def get_all_images(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM images")

        rows = cursor.fetchall()

        readings = [
            DetectionImage(id=row[0], path=row[1], timestamp=row[2]) for row in rows
        ]

        return readings

    def get_img_by_id(self, id):
        try:
            cursor = self.conn.cursor()

            cursor.execute(f"SELECT * FROM images where id = {id}")

            rows = cursor.fetchall()

            readings = [
                DetectionImage(id=row[0], path=row[1], timestamp=row[2]) for row in rows
            ]
            print("path: ", readings[0].path)
            return readings[0]
        except Exception as e:
            print("Error fetching image: ", e)

    def get_last_image(self):
        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT * FROM images ORDER BY id DESC LIMIT 1;")

            row = cursor.fetchone()

            res = DetectionImage(id=row[0], path=row[1], timestamp=row[2])

            return res
        except Exception as e:
            print("Error al buscar ultima imagen: ", e)
            
    def get_last_fall_detected_img(self) -> DetectionImage:
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT images.* FROM images
                JOIN fall_detection ON images.id = fall_detection.img_id
                WHERE fall_detection.fall_detected = true
                ORDER BY fall_detection.timestamp DESC LIMIT 1;
            """)

            row = cursor.fetchone()

            if row:
                res = DetectionImage(id=row[0], path=row[1], timestamp=row[2])
                return res
            else:
                print("No fall detected images found.")
                return None
        except Exception as e:
            print("Error fetching the last fall-detected image: ", e)


    def get_cv_reading_from_img_id(self, img_id):
        try:
            cursor = self.conn.cursor()

            cursor.execute(f"SELECT * FROM fall_detection where img_id = {img_id}")

            row = cursor.fetchone()

            res = FallCameraReading(
                id=row[0],
                timestamp=row[1],
                fall_detected=row[2],
                confidence=row[3],
                num_people_detected=row[4],
                img_id=row[5]
            )


            return res
        except Exception as e:
            print("Error al buscar ultima imagen: ", e)
            
    def insert_emotion_detection(self, emotion_detection: EmotionDetection):
        try:
            cursor = self.conn.cursor()
            
            # Cambiar el nombre de la tabla y corregir nombres de columnas
            query = """
            INSERT INTO emotion_detection 
            (timestamp, img_id, dominant_emotion, angry_probability, disgust_probability, fear_probability, happy_probability, neutral_probability, sad_probability, surprise_probability, video_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Asegúrate de pasar los valores correctos en el orden correcto
            cursor.execute(
                query, 
                (
                    emotion_detection.timestamp,
                    emotion_detection.img_id,
                    emotion_detection.dominant_emotion,
                    emotion_detection.angry_probability,
                    emotion_detection.disgust_probability,
                    emotion_detection.fear_probability,
                    emotion_detection.happy_probability,
                    emotion_detection.neutral_probability,
                    emotion_detection.sad_probability,
                    emotion_detection.surprise_probability,
                    emotion_detection.video_id
                )
            )
            
            self.conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al insertar detección de emociones: {e}")

    
    def create_emotion_detection_video(self, video_path, uuid):
        try:
            cursor = self.conn.cursor()
            
            cursor.execute(
                "INSERT INTO emotion_videos (path, uuid) VALUES (%s, %s) RETURNING id", (video_path, uuid)
            )
            video_id = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return video_id
        except Exception as e:
            print(f"Error al insertar video: {e}")
            
    def analyze_emotions_by_video_id(self, video_id):
        try:
            cursor = self.conn.cursor()
            
            # Consulta para obtener todas las filas relacionadas con el video_id
            query = """
            SELECT 
                ev.uuid,
                e.dominant_emotion,
                e.angry_probability,
                e.disgust_probability,
                e.fear_probability,
                e.happy_probability,
                e.neutral_probability,
                e.sad_probability,
                e.surprise_probability
            FROM emotion_detection e
            JOIN emotion_videos ev ON e.video_id = ev.id
            WHERE e.video_id = %s
            """
            
            cursor.execute(query, (video_id,))
            results = cursor.fetchall()
            
            if not results:
                print(f"No se encontraron registros para el video_id: {video_id}")
                return None

            # Inicializar variables para calcular promedios y recolectar UUID
            total_angry = total_disgust = total_fear = total_happy = 0
            total_neutral = total_sad = total_surprise = 0
            count = 0
            dominant_emotion_counts = {}
            video_uuid = None  # Será el mismo para todas las filas, ya que proviene de emotions_videos
            
            for row in results:
                video_uuid = row[0]
                dominant_emotion = row[1]
                angry_prob = row[2]
                disgust_prob = row[3]
                fear_prob = row[4]
                happy_prob = row[5]
                neutral_prob = row[6]
                sad_prob = row[7]
                surprise_prob = row[8]
                
                # Sumar las probabilidades para calcular el promedio después
                total_angry += angry_prob
                total_disgust += disgust_prob
                total_fear += fear_prob
                total_happy += happy_prob
                total_neutral += neutral_prob
                total_sad += sad_prob
                total_surprise += surprise_prob
                count += 1

                # Contar las emociones dominantes para determinar la más frecuente
                dominant_emotion_counts[dominant_emotion] = dominant_emotion_counts.get(dominant_emotion, 0) + 1

            # Calcular promedios de las probabilidades
            avg_angry = total_angry / count
            avg_disgust = total_disgust / count
            avg_fear = total_fear / count
            avg_happy = total_happy / count
            avg_neutral = total_neutral / count
            avg_sad = total_sad / count
            avg_surprise = total_surprise / count

            # Determinar la emoción dominante más frecuente
            most_frequent_emotion = max(dominant_emotion_counts, key=dominant_emotion_counts.get)
            
            cursor.close()
            
            # Construir el análisis final
            analysis = {
                "video_id": video_id,
                "video_uuid": video_uuid,
                "average_probabilities": {
                    "avg_angry": avg_angry,
                    "avg_disgust": avg_disgust,
                    "avg_fear": avg_fear,
                    "avg_happy": avg_happy,
                    "avg_neutral": avg_neutral,
                    "avg_sad": avg_sad,
                    "avg_surprise": avg_surprise
                },
                "most_frequent_emotion": most_frequent_emotion
            }
            
            return analysis
        except Exception as e:
            print(f"Error al analizar las emociones para el video_id {video_id}: {e}")
            return None


    def get_all_emotion_videos(self):
        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT * FROM emotion_videos")

            rows = cursor.fetchall()

            readings = [
               EmotionDetectionVideo(
                   id=row[0],
                   path=row[1],
                   timestamp=row[2],
                   uuid=row[3]
               )
               for row in rows
            ]

            return readings
        
        except Exception as e:
            print("Error getting all emotions: ", e)