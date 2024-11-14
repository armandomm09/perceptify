from configparser import ConfigParser
import psycopg2
from data_models import BeltReading, FallCameraReading, DetectionImage


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
                    image_id=row[5]
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

    def insert_cv_reading(self, reading: FallCameraReading):
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
                    reading.image_id,
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
                image_id=row[5]
            )

            return res
        except Exception as e:
            print("Error al buscar ultima imagen: ", e)
