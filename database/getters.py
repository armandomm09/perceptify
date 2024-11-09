

def get_all_belt_readings(conn):
    
    cur = conn.cursor()

    cur.execute("SELECT * FROM belt_reading")

    rows = cur.fetchall()

    for row in rows:
        print(row)
        
    cur.close()