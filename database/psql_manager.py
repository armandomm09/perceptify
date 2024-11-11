from configparser import ConfigParser
import psycopg2
from data_models import BeltReading, FallCameraReading


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
            )
            for row in rows
        ]

        return readings

    def insert_belt_reading(self, reading: BeltReading):
        try:
            cursor = self.conn.cursor()

            query = """
            INSERT INTO belt_reading (timestamp, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                )
            )
            self.conn.commit()
            cursor.close()
        except Exception as e:
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
             num_people_detected=row[4]
         ) 
         for row in rows  
        ]
        return readings
    
    def insert_cv_reading(self, reading: FallCameraReading):
        try:
            cursor = self.conn.cursor()
            
            query = """
            INSERT INTO fall_detection (timestamp, fall_detected, confidence, num_people_detected)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(
                query, 
                (
                    reading.timestamp,
                    reading.fall_detected,
                    reading.confidence,
                    reading.num_people_detected
                )
            )
            
            self.conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al insertar datos en fall_detection: {e}")