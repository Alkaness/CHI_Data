import sqlite3

connection = sqlite3.connect("data/weather.db")
cursor = connection.cursor()
cursor.execute("select * from weather_daily")
results = cursor.fetchall()
for row in results:
    print(row)

connection.close()
