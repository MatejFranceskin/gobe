import re
import sys
from unidecode import unidecode
import sqlite3
import locale

def extractOSGS2013():
    file = open('osgs2013.txt', mode="r", encoding="utf-8")
    list = []
    for line in file.readlines():
        sline = line.strip()
        if line.startswith("\t"):
            continue
        if not line.startswith("  ") or not sline:
            continue
        if not sline.split('.')[0].isnumeric():
            list[-1] += " " + sline
            continue
        list.append(sline)

    for l in list:
        l = re.sub("[\(\[].*?[\)\]]", "", l)
        l = l.replace(" ex ", " ").replace(" & ", " ")
        words = l.split()
        name = words[1] + " " + words[2]
        wi = 3
        if words[3] == "var.":
            name += " var. " + words[4]
            wi = 5
        slo_name = ""
        for i in range(wi, len(words)):
            if words[i].lower() != words[i] or words[i].replace(',', '').isnumeric():
                continue
            slo_name += words[i] + " "

        imenaOSGS2013.append((unidecode(name.strip()), slo_name.strip()))

rod = sys.argv[1]

wiki_out = []

imenaOSGS2013 = []
extractOSGS2013()

for i in imenaOSGS2013:
    if i[0].startswith(rod):
        wiki_out.append("*[[{}|{} (''{}'')]]".format(i[1], i[1], i[0]))
        
conn = sqlite3.connect('gobe.db')
cursor = conn.cursor()

utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)

cursor.execute("SELECT name, name_slo FROM vrste WHERE name like '%{}%' ORDER BY name_slo".format(rod))
records = cursor.fetchall()
for row in records:
    wiki_out.append("*[[{}|{} (''{}'')]]".format(row[1], row[1], row[0]))


wiki_out = list(set(wiki_out))
locale.setlocale(locale.LC_ALL, "")
wiki_out.sort(key=locale.strxfrm)

for w in wiki_out:
    print(w)
