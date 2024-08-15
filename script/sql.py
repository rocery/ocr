import mysql.connector
from datetime import datetime
import re

# Function to normalize no_mobil
def normalize_no_mobil(no_mobil):
    # Remove spaces and uppercase all letters
    return re.sub(r'\s+', '', no_mobil).upper()

# Function to fetch ekspedisi based on normalized no_mobil
def get_ekspedisi(no_mobil):
    # Normalize no_mobil for comparison
    no_mobil_normalized = normalize_no_mobil(no_mobil)
    
    # Connect to the parkir database to get the ekspedisi
    conn_parkir = mysql.connector.connect(
        host='192.168.15.220',
        user='user_external_220',
        password='Sttbekasioke123!',
        database='parkir'
    )
    cursor_parkir = conn_parkir.cursor()
    
    # Fetch the ekspedisi name using normalized no_mobil
    cursor_parkir.execute("""
        SELECT nama_ekspedisi FROM pengukuran
        WHERE REPLACE(REPLACE(nomor_polisi, ' ', ''), '-', '') = %s
    """, (no_mobil_normalized,))
    result = cursor_parkir.fetchone()
    
    cursor_parkir.close()
    conn_parkir.close()
    
    if result:
        return result[0]
    else:
        return None

# Connect to MySQL for the main operations
conn = mysql.connector.connect(
    host='192.168.15.223',
    user='admin',
    password='itbekasioke',
    database='iot'
)
cursor = conn.cursor()

# Function to handle "masuk" (entry)
def masuk(tanggal, no_mobil, jam_masuk_pabrik, user_in):
    # Normalize no_mobil for consistency
    no_mobil_normalized = normalize_no_mobil(no_mobil)
    ekspedisi = get_ekspedisi(no_mobil_normalized)
    
    if not ekspedisi:
        print(f"Ekspedisi not found for vehicle {no_mobil_normalized}. Proceeding with entry.")
        ekspedisi = None

    # Check if the vehicle is already in the database with incomplete exit data
    cursor.execute("""
        SELECT * FROM test
        WHERE no_mobil = %s AND (tanggal_keluar IS NULL OR jam_keluar IS NULL)
    """, (no_mobil_normalized,))
    result = cursor.fetchone()

    if result:
        print(f"Vehicle {no_mobil_normalized} is already inside and has not exited yet.")
        return

    # Insert new entry with normalized no_mobil
    cursor.execute("""
        INSERT INTO test (tanggal, no_mobil, jam_masuk_pabrik, user_in, ekspedisi)
        VALUES (%s, %s, %s, %s, %s)
    """, (tanggal, no_mobil_normalized, jam_masuk_pabrik, user_in, ekspedisi))
    conn.commit()
    print(f"Vehicle {no_mobil_normalized} has entered with ekspedisi {ekspedisi if ekspedisi else 'N/A'}.")

# Function to handle "keluar" (exit)
def keluar(no_mobil, jam_keluar, user_out):
    # Normalize no_mobil for consistency
    no_mobil_normalized = normalize_no_mobil(no_mobil)
    
    # Check if the vehicle has an entry record without an exit
    cursor.execute("""
        SELECT * FROM test
        WHERE no_mobil = %s AND tanggal_keluar IS NULL AND jam_masuk_pabrik IS NOT NULL
    """, (no_mobil_normalized,))
    result = cursor.fetchone()

    if not result:
        print(f"No entry found for vehicle {no_mobil_normalized}, or it has already exited.")
        return

    # Update record with exit information
    cursor.execute("""
        UPDATE test
        SET tanggal_keluar = %s, jam_keluar = %s, user_out = %s
        WHERE no_mobil = %s AND tanggal_keluar IS NULL
    """, (datetime.now().date(), jam_keluar, user_out, no_mobil_normalized))
    conn.commit()
    print(f"Vehicle {no_mobil_normalized} has exited.")

# Example usage
# masuk('2024-08-15', 'A413XCA', '08:56:12', 'SASTRA')
keluar('B9145IW', '12:34:56', 'ADI')

# Close the connection
cursor.close()
conn.close()
