

def insert_belt_reading(conn, timestamp, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z):
    try:
        cursor = conn.cursor()
        
        query = """
        INSERT INTO belt_reading (timestamp, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (timestamp, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z))
        
        conn.commit()
        
        print("Datos insertados correctamente.")
        
        cursor.close()
    except Exception as e:
        print(f"Error al insertar los datos: {e}")