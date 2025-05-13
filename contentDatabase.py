import sqlite3

connection = sqlite3.connect('./database.db')
cursor = connection.cursor()
cursor.execute('PRAGMA table_info(FrequencyData)')
columns = cursor.fetchall()

for column in columns:
    print(column)
connection.close()
