import sqlite3
import re
import sys

conn = sqlite3.connect('gobe.db')

cursor = conn.cursor()

with open('gobe.csv', mode="r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
        a = line.split(',')
        comment = "";
        for i in range(4, len(a)):
            if len(comment) > 0:
                comment += ", "
            comment += a[i].strip()
        s = "UPDATE vrste SET comment = '{}' WHERE name = '{}'".format(comment, a[0].strip()).replace("\"", "")
        cursor.execute(s)
        cursor.execute("SELECT id FROM vrste WHERE name = '{}'".format(a[0].strip()))
        data = cursor.fetchall()
        for d in data:
            cursor.execute('INSERT INTO slike(vrsta_id, link, author) VALUES(?,?,?)', (d[0], a[3], "quiz"))
                
#sqlite_select_query = '''SELECT * FROM slike'''
#cursor.execute(sqlite_select_query)
#records = cursor.fetchall()
#print("Total rows are:  ", len(records))
#for row in records:
#    sys.stdout.buffer.write(row[2].encode('utf8'))
#    sys.stdout.buffer.write(' '.encode('utf8'))
#    sys.stdout.buffer.write(row[3].encode('utf8'))
#    sys.stdout.buffer.write('\n'.encode('utf8'))

cursor.close()
conn.commit()
conn.close()
