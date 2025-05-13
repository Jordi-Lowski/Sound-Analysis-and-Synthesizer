import sqlite3

db_path = './database.db'

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute('''
ALTER TABLE FrequencyData ADD COLUMN type TEXT
''')

connection.commit()
connection.close()
print("Colum 'type' was successfully added.")
