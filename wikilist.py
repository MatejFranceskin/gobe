#Seznam gliv Slovenije je narejen na osnovi seznama gliv s slovenskimi imeni Gobarskega društva Lisička Maribor.<ref>{{Navedi splet|title=Spisek gob na gobe.si po latinskih imenih - Gobarsko društvo Lisička Maribor|url=https://www.gobe.si/Gobe|website=www.gobe.si|accessdate=2024-03-09}}</ref>

#[[Kategorija:Glive]]
#[[Kategorija:Seznami gliv|Seznam gliv Slovenije]]


import sqlite3
from unidecode import unidecode

conn = sqlite3.connect('gobe.db')
cursor = conn.cursor()

#sqlite_select_query = '''SELECT id,name,name_slo,status,protected,link FROM vrste ORDER BY name ASC'''
sqlite_select_query = '''SELECT id,name,name_slo,status,protected,link FROM vrste WHERE status != "" OR protected > 0 ORDER BY name ASC'''
cursor.execute(sqlite_select_query)
records = cursor.fetchall()

utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)

print('{| class="wikitable sortable"', file=utf8stdout)
print('! znanstveno ime', file=utf8stdout)
print('! slovensko ime', file=utf8stdout)
print('! Stanje ogroženosti', file=utf8stdout)
print('! class="unsortable" | Slika', file=utf8stdout)

for row in records:
    if "Protozoa" in str(row[5]):
        continue

    slika = ""
    cursor.execute('''SELECT link FROM slike WHERE vrsta_id==? AND author="wikimedia"''', (row[0],))
    links = cursor.fetchall()
    for link in links:
        slika = link[0]
        break

    print('|-', file=utf8stdout)
    print('|'+row[1], file=utf8stdout)
    print('|[['+row[2].replace("ó", "o")+']]', file=utf8stdout)

    status = ""
    if row[3] == "E":
        status = "prizadeta"
    elif row[3] == "V":
        status = "ranljiva"
    elif row[3] == "R":
        status = "redka"
    elif row[3]:
        status = "ogrožena"
    if row[4]:
        if status:
            status += ", "
        status += "zavarovana"
    print('|'+status, file=utf8stdout)

    part = slika.encode('utf-8').decode('unicode_escape').partition("File:")
    if len(part) > 2 and part[1] and part[2]:
        print('|[['+part[1]+part[2]+'|frameless|thumb]]', file=utf8stdout)
    else:
        print('|', file=utf8stdout)

print('|}', file=utf8stdout)

cursor.close()
conn.close()
