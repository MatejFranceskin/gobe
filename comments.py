import sqlite3
import re

conn = sqlite3.connect('gobe.db')

cursor = conn.cursor()

with open('gobe.csv', 'r') as f:
    lines = f.readlines()
    for line in lines:
        a = line.split(',')
        comment = "";
        for i in range(3, len(a)):
            if len(comment) > 0:
                comment += ", "
            comment += a[i].strip()
        s = "UPDATE vrste SET comment = '{}' WHERE name = '{}'".format(comment, a[0].strip()).replace("\"", "")
        cursor.execute(s)

cursor.close()
conn.commit()
conn.close()
