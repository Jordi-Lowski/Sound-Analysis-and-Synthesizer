import sqlite3
import os

db_path = 'database.db'
folder_paths = ['Data/AcousticGuitar', 'Data/WesternGuitar']

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

for folder_path in folder_paths:
    if 'AcousticGuitar' in folder_path:
        guitar_type = 'acoustic'
    elif 'WesternGuitar' in folder_path:
        guitar_type = 'western'
    else:
        continue 
    for filename in os.listdir(folder_path):
        if filename.endswith(".mat"):
            try:
                cursor.execute('''
                    UPDATE FrequencyData
                    SET type = ?
                    WHERE file_name = ?
                ''', (guitar_type, filename))
                connection.commit()  
                print(f"Updated type for {filename} to {guitar_type}")
            except Exception as e:
                print(f"Error updating {filename}: {e}")

connection.close()
