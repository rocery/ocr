import mysql.connector
from datetime import datetime
import re
import csv


# Function to connect to the iot database
def get_tparkir_connection():
    return mysql.connector.connect(
        host='192.168.15.223',
        user='admin',
        password='itbekasioke',
        database='iot'
    )

def get_tparkir_connection_220():
    return mysql.connector.connect(
        host='192.168.15.220',
        user='user_external_220',
        password='Sttbekasioke123!',
        database='parkir'
    )

# Function to normalize no_mobil
def normalize_no_mobil(no_mobil):
    return re.sub(r'\s+', '', no_mobil).upper()

# Function to fetch ekspedisi based on normalized no_mobil
def get_ekspedisi(no_mobil):
    no_mobil_normalized = normalize_no_mobil(no_mobil)
    
    conn_parkir = mysql.connector.connect(
        host='192.168.15.220',
        user='user_external_220',
        password='Sttbekasioke123!',
        database='parkir'
    )
    cursor_parkir = conn_parkir.cursor()
    
    cursor_parkir.execute("""
        SELECT nama_ekspedisi FROM pengukuran
        WHERE REPLACE(REPLACE(nomor_polisi, ' ', ''), '-', '') = %s
    """, (no_mobil_normalized,))
    result = cursor_parkir.fetchone()
    
    cursor_parkir.close()
    conn_parkir.close()
    
    return result[0] if result else None

def masuk_220(tanggal, no_mobil, jam_masuk_pabrik, user_in):
    conn = get_tparkir_connection_220()
    
    ekspedisi = get_ekspedisi(no_mobil)
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tparkir (tanggal, no_mobil, jam_masuk_pabrik, user_in, ekspedisi)
            VALUES (%s, %s, %s, %s, %s)
        """, (tanggal, no_mobil, jam_masuk_pabrik, user_in, ekspedisi))
        conn.commit()
        return "Success"
    except mysql.connector.Error as err:
        conn.rollback()  # rollback in case of failure
        return f"Failed: {err}"
    
def keluar_220(no_mobil, tanggal_keluar, jam_keluar, user_out):
    conn = get_tparkir_connection_220()
    
    try:
        cursor = conn.cursor()
        no_mobil_normalized = normalize_no_mobil(no_mobil)
        
        # Fetch entry for the vehicle that hasn't exited yet and has entered the factory
        cursor.execute("""
            SELECT * FROM tparkir
            WHERE no_mobil = %s AND tanggal_keluar IS NULL AND jam_masuk_pabrik IS NOT NULL
        """, (no_mobil_normalized,))
        result = cursor.fetchone()

        if not result:
            print(f"No entry found for vehicle {no_mobil_normalized}, or it has already exited.")
            return "outside"

        # Update the entry with exit details
        cursor.execute("""
            UPDATE tparkir
            SET tanggal_keluar = %s, jam_keluar = %s, user_out = %s
            WHERE no_mobil = %s AND tanggal_keluar IS NULL
        """, (tanggal_keluar, jam_keluar, user_out, no_mobil_normalized))
        
        conn.commit()
        print(f"Vehicle {no_mobil_normalized} has exited.")
        return "inside"

    except mysql.connector.Error as err:
        # Handle any error and rollback
        conn.rollback()
        print(f"Error occurred: {err}")
        return f"Failed: {err}"
    
    finally:
        cursor.close()  # Ensure the cursor is always closed
    

# Function to handle "masuk" (entry)
def masuk(conn, tanggal, no_mobil, jam_masuk_pabrik, user_in):
    cursor = conn.cursor()
    no_mobil_normalized = normalize_no_mobil(no_mobil)
    ekspedisi = get_ekspedisi(no_mobil_normalized)
    status = None
    
    if not ekspedisi:
        print(f"Ekspedisi not found for vehicle {no_mobil_normalized}. Proceeding with entry.")
        ekspedisi = None
        status = "noeks"

    cursor.execute("""
        SELECT * FROM ocr
        WHERE no_mobil = %s AND (tanggal_keluar IS NULL OR jam_keluar IS NULL)
    """, (no_mobil_normalized,))
    result = cursor.fetchone()

    if result:
        print(f"Vehicle {no_mobil_normalized} is already inside and has not exited yet.")
        status = "inside"
        return status

    cursor.execute("""
        INSERT INTO ocr (tanggal, no_mobil, jam_masuk_pabrik, user_in, ekspedisi)
        VALUES (%s, %s, %s, %s, %s)
    """, (tanggal, no_mobil_normalized, jam_masuk_pabrik, user_in, ekspedisi))
    conn.commit()
    
    if status == "noeks":
        print(f"Vehicle {no_mobil_normalized} has entered without ekspedisi.")
        return status
    
    print(f"Vehicle {no_mobil_normalized} has entered with ekspedisi {ekspedisi if ekspedisi else 'N/A'}.")
    status = ekspedisi
    return status
    
# Function to handle "keluar" (exit)
def keluar(conn, no_mobil, tanggal_keluar, jam_keluar, user_out):
    cursor = conn.cursor()
    no_mobil_normalized = normalize_no_mobil(no_mobil)
    status = None
    
    cursor.execute("""
        SELECT * FROM ocr
        WHERE no_mobil = %s AND tanggal_keluar IS NULL AND jam_masuk_pabrik IS NOT NULL
    """, (no_mobil_normalized,))
    result = cursor.fetchone()

    if not result:
        print(f"No entry found for vehicle {no_mobil_normalized}, or it has already exited.")
        status = "outside"
        return status

    cursor.execute("""
        UPDATE ocr
        SET tanggal_keluar = %s, jam_keluar = %s, user_out = %s
        WHERE no_mobil = %s AND tanggal_keluar IS NULL
    """, (tanggal_keluar, jam_keluar, user_out, no_mobil_normalized))
    conn.commit()
    print(f"Vehicle {no_mobil_normalized} has exited.")
    status = "inside"
    return status

def readCSV(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)

def get_data_ocr():
    conn = get_tparkir_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            CONCAT(tanggal, ' ', jam_masuk_pabrik) AS waktu_masuk,
            no_mobil,
            ekspedisi,
            keperluan,
            CONCAT(tanggal_keluar, ' ', jam_keluar) AS waktu_keluar
        FROM 
            ocr
        ORDER BY tanggal DESC, jam_masuk_pabrik DESC
        LIMIT 100
    """)
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    print(result)
    return result

def keperluan(label, keperluan):
    try:
        conn = get_tparkir_connection()
        cursor = conn.cursor()

        # Step 1: Get the latest tanggal for the given no_mobil
        cursor.execute("""
            SELECT MAX(tanggal) 
            FROM ocr 
            WHERE no_mobil = %s
        """, (label,))
        latest_date = cursor.fetchone()[0]

        if latest_date is None:
            return False  # No record found for the given no_mobil
        
        # Step 2: Get the latest time for the given no_mobil
        cursor.execute("""
            SELECT MAX(jam_masuk_pabrik) 
            FROM ocr 
            WHERE no_mobil = %s
            AND tanggal = %s
        """, (label, latest_date))
        latest_time = cursor.fetchone()[0]

        if latest_time is None:
            return False  # No record found for the given no_mobil
        
        print(latest_date)
        print(latest_time)

        # Step 2: Update the record with the latest tanggal
        cursor.execute("""
            UPDATE ocr
            SET keperluan = %s
            WHERE no_mobil = %s
            AND tanggal = %s
            AND jam_masuk_pabrik = %s
        """, (keperluan, label, latest_date, latest_time))
        
        conn.commit()
        
        # Mengecek jumlah baris yang terpengaruh
        if cursor.rowcount > 0:
            return True
        else:
            return False

    except mysql.connector.Error as err:
        print(f"Errors: {err}")
        return "Error"
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    
# Example usage in another script
# if __name__ == "__main__":
#     conn = get_tparkir_connection()

#     a = 'BE8709OU'
#     # Perform "masuk" operation
#     masuk(conn, '2024-08-15', a, '08:56:12', 'SASTRA')

#     # Perform "keluar" operation with a custom tanggal_keluar
#     custom_tanggal_keluar = datetime(2024, 8, 15).date()  # You can set this to any date
#     keluar(conn, a, custom_tanggal_keluar, '12:34:56', 'ADI')

#     conn.close()
