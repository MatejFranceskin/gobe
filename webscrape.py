import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from unidecode import unidecode
import time 
import pandas as pd 
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By 

def url_request(url):
    while True:
        try:
            print("Getting " + url)
            response = requests.get(url, headers={"User-Agent": "Chrome/112.0.0.0"})
            return response
        except:
            print("Retrying " + url)

def processSlikaURL(vrsta_id, url, author):
    print(url)
    cursor.execute("SELECT id FROM slike WHERE link = ?", (url,))
    data = cursor.fetchall()
    if len(data) == 0:
        cursor.execute('INSERT INTO slike(vrsta_id, link, author) VALUES(?,?,?)', (vrsta_id, url, author))

def extractFromSlikeURL(vrsta_id, name):
    n = name.split()
    url = "https://www.gobe.si/Slike/" + n[0] + n[1].capitalize().replace("-judae", "-Judae")
    response = url_request(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('td')

        author = ""
        divs = soup.find_all('div')
        for div in divs:
            ss = soup.find_all('small')
            c = ss[0].get_text().strip()
            if c.startswith("Foto:"):
                author = c
                break
        imgs = soup.find_all('img')
        for img in imgs:
            url = img.get('src')
            if (url.startswith("/slike/") and url.endswith(".jpg")):
                processSlikaURL(vrsta_id, "https://www.gobe.si" + url, author)

        for row in rows:
            arr = []
            lines = row.get_text().splitlines()
            author = ""
            url = ""
            for line in lines:
                l = line.strip()
                if l.startswith("Foto:"):
                    author = l
                    break
            links = row.find_all('img')
            for link in links:
                processSlikaURL(vrsta_id, "https://www.gobe.si/slike/" + link.get('src').removeprefix("/slikethumb/thumb_"), author)
                break

    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)

def extractFromSeznamURL(url, mark):
    response = url_request(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('td')
        for row in rows:
            arr = []
            lines = row.get_text().splitlines()
            for line in lines:
                l = line.strip()
                if l:
                    arr.append(l)
            links = row.find_all('a')
            for link in links:
                arr.append(link.get('href'))
                
            cursor.execute("SELECT id FROM vrste WHERE name = ?", (arr[0],))
            data = cursor.fetchall()
            if len(data) == 0:
                name_slo = arr[1].strip().replace('(', '').replace(')', '')
                s = "INSERT INTO vrste(name, name_slo, edibility, link, {}) VALUES('{}','{}','{}','{}',1)".format(mark, arr[0], name_slo, arr[2], arr[3].strip())
                cursor.execute(s)
            else:
                s = "UPDATE vrste SET {} = 1, edibility = '{}' WHERE name = '{}'".format(mark, arr[2], arr[0])
                cursor.execute(s)
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
    conn.commit()

def extractFromCelotniSeznamURL(url):
    response = url_request(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('li')
        for row in rows:
            arr = []
            lines = row.get_text().splitlines()
            for line in lines:
                l = line.replace('(', '').replace(')', '').strip()
                a = l.split(',')
                if len(a) != 2:
                    continue
                ln = a[0].strip().split()
                if len(ln) < 2:
                    continue
                sn = a[1].strip().split()
                if len(sn) < 2:
                    continue
                arr.append(ln[0] + " " + ln[1])
                arr.append(sn[0] + " " + sn[1])
            if len(arr) == 0:
                continue
            links = row.find_all('a')
            for link in links:
                arr.append(link.get('href'))

            cursor.execute("SELECT id FROM vrste WHERE name = ?", (arr[0],))
            data = cursor.fetchall()
            if len(data) == 0:
                s = "INSERT INTO vrste(name, name_slo, link) VALUES('{}','{}','{}')".format(arr[0], arr[1], arr[2].strip())
                cursor.execute(s)
                print(s)
            else:
                s = "UPDATE vrste SET name_slo = '{}',link='{}' WHERE name = '{}'".format(arr[1], arr[2].strip(), arr[0])
                cursor.execute(s)
                print(s)

def extractFromRdeciSeznamURL(url):
    response = url_request(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('li')
        for row in rows:
            arr = []
            lines = row.get_text().splitlines()
            for line in lines:
                l = line.strip()
                if "kategorija" not in l:
                    continue
                if l:
                    fields = l.split(",")
                    arr.append(fields[0])
                    a = fields[1].strip().split()
                    arr.append(a[0] + " " + a[1])
                    for i in range(2, len(fields)):
                        b = fields[i].strip().split()
                        if b[0] == "kategorija":
                            arr.append(b[2])
            if len(arr) == 0:
                continue
            links = row.find_all('a')
            for link in links:
                arr.append(link.get('href'))

            cursor.execute("SELECT id FROM vrste WHERE name = ?", (arr[0],))
            data = cursor.fetchall()

            if len(data) == 0:
                name_slo = arr[1].strip().replace('(', '').replace(')', '')
                s = "INSERT INTO vrste(name, name_slo, status, link) VALUES('{}','{}','{}','{}')".format(arr[0], name_slo, arr[2], arr[3].strip())
                cursor.execute(s)
            else:
                s = "UPDATE vrste SET status = '{}' WHERE name = '{}'".format(arr[2], arr[0])
                cursor.execute(s)
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
    conn.commit()

def extractFromZasciteniSeznamURL(url):
    response = url_request(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('li')
        for row in rows:
            arr = []
            links = row.find_all('a')
            for link in links:
                s = "UPDATE vrste SET protected = 1 WHERE link = '{}'".format(link.get('href'))
                cursor.execute(s)
                break
    conn.commit()

def extractUzitnostUrl(url, id, name):
    response = url_request(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('p')
        for row in rows:
            srow = str(row)
            if "UPORABNOST" in srow or "STRUPENOST" in srow:
                srow = srow.removeprefix('<p class="vspace">').replace('<strong>', '').replace('</strong>', '').replace('</p>', '').replace('<span class="-pm--3">', '').replace('</span>', '').strip()
                srow = srow.removeprefix('UPORABNOST: ').removeprefix('STRUPENOST: ')
                edibility = srow.lower().strip()
                if edibility.startswith("užitnost neznana"):
                    edibility = "užitnost neznana"
                elif edibility.startswith("neznana"):
                    edibility = "užitnost neznana"
                elif edibility.startswith("užitnost ni znana"):
                    edibility = "užitnost neznana"
                elif edibility.startswith("pogojno užit"):
                    edibility = "pogojno užitna"
                elif edibility.startswith("kuhana je užitna"):
                    edibility = "pogojno užitna"
                elif (edibility.startswith("smrtno strupen")):
                    edibility = "smrtno strupena"
                elif (edibility.startswith("strupena")):
                    edibility = "strupena"
                elif (edibility.startswith("strupna")):
                    edibility = "strupena"
                elif (edibility.startswith("neužitna; vsebuje strupe")):
                    edibility = "strupena"
                elif (edibility.startswith("neužit")):
                    edibility = "neužitna"
                elif (edibility.startswith("mlada užitna")):
                    edibility = "mlada užitna"
                elif (edibility.startswith("mlad je užiten")):
                    edibility = "mlada užitna"
                elif (edibility.startswith("užitna")):
                    edibility = "užitna"
                elif (edibility.startswith("užiten")):
                    edibility = "užitna"
                elif (edibility.startswith("zelo dobra užitna goba")):
                    edibility = "užitna"
                elif (edibility.startswith("užitni so klobuki")):
                    edibility = "užitna"
                elif (edibility.startswith("dobra")):
                    edibility = "užitna"
                elif (edibility.startswith("odlična")):
                    edibility = "užitna"
                elif (edibility.startswith("sicer užitna")):
                    edibility = "užitna"
                elif (edibility.startswith("goba je sicer veljala za užitno")):
                    edibility = "neužitna"
                elif "vsebuje smrtno nevarno snov" in edibility:
                    edibility = "smrtno strupena"
                elif (edibility.startswith("ni zelo strupena")):
                    edibility = "strupena"
                elif (edibility.startswith("opredeljena sicer kot užitna, vendar ker vsebuje halucinogene snovi")):
                    edibility = "strupena"
                elif (edibility.startswith("surova strupena. šele po dolgotrajnem")):
                    edibility = "strupena"
                else:
                    print(edibility)
                    exit()
                s = "UPDATE vrste SET edibility = '{}' WHERE id = {}".format(edibility, id)
#                print(s)
                cursor.execute(s)

        conn.commit()

def checkUzitnost():
    cursor.execute('''SELECT id,link,name FROM vrste WHERE edibility = ""''')
    records = cursor.fetchall()
    for row in records:
        extractUzitnostUrl(row[1], row[0], row[2])

def checkSlike():
    cursor.execute('''SELECT id, name FROM vrste''')
    records = cursor.fetchall()
    for record in records:
        cursor.execute('''SELECT id FROM slike WHERE vrsta_id = ?''', (record[0],))
        if not cursor.fetchall():
            extractFromSlikeURL(record[0], record[1])
    conn.commit()

def extractFromMycobank(id):
    options = webdriver.ChromeOptions() 
    options.add_argument("--headless")
    options.page_load_strategy = "none"
    driver = Chrome(options=options)
    url = 'https://www.mycobank.org/page/Name%20details%20page/field/Mycobank%20%23/' + id
    driver.get(url) 
    time.sleep(5)
    page = driver.page_source
    i = page.find("Current name")
    if (i >= 0):
        j = page.find("<span", i)
        if (j >= 0):
            k = page.find(">", j)
            if (k >= 0):
                l = page.find("</span>", k)
                if (l >= 0):
                    name = page[k+1:l]
                    return name
    driver.close()
    return ""

def extractOSGS2013():
    first_index = 0;
    with open('osgs2013.csv', 'r') as csvfile:
        csv = csvfile.readlines()
        fi = csv[-1].split(";")[0]
        first_index = int(fi.split(".")[0])

    file = open('OSGS__20130907.txt', 'r')
    lines = file.readlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == "":
            i += 1
            continue
        if lines[i + 2].strip().startswith("SGS98"):
            i += 7
            continue
        index = lines[i].strip()
        id_if = lines[i + 1].strip()
        sgs98 = lines[i + 2].strip()
        if sgs98.endswith(","):
            sgs98 += " " + lines[i + 3].strip()
            i += 1
        old_lat_name = lines[i + 3].strip()
        old_slo_name = lines[i + 4].strip()
        if old_slo_name.endswith(",") or lines[i + 5].strip().startswith("razl"):
            old_slo_name += " " + lines[i + 5].strip()
            i += 1
        status = lines[i + 5].strip()
        ostala_imena = lines[i + 6].strip()
        if ostala_imena.endswith(","):
            ostala_imena += " " + lines[i + 7].strip()
            i += 1
        if not lines[i + 7].strip().endswith("."):
            ostala_imena += " " + lines[i + 7].strip()
            i += 1
        words = old_lat_name.split()
        if len(words) < 3:
            break
        old_lat_name = words[0] + " " + words[1]
        if words[2] == "var.":
            old_lat_name += " var. " + words[3]

        i += 7

        if (int(index.split(".")[0]) <= first_index):
#            print("Skipping " + index + " " + id_if)
            continue

        while True:
            if id_if in ["205150", "171303", "355892", "544424", "461558"]:
                lat_name = unidecode(old_lat_name) + " x"
            else:
                lat_name = extractFromMycobank(id_if)
            words = lat_name.split()
            if len(words) > 2:
                break
            print("Retrying " + old_lat_name + " " + id_if)

        lat_name = words[0] + " " + words[1]
        if len(words) > 2 and words[2] == "var.":
            lat_name += " var. " + words[3]
        entry = index + ";" + id_if + ";" + sgs98 + ";" + lat_name + ";" + old_lat_name + ";" + old_slo_name + ";" + status + ";" + ostala_imena            
        print(entry)    
        with open('osgs2013.csv', 'a') as csvfile:
            csvfile.write(entry + "\n")

    with open('osgs2013.csv', 'r') as csvfile:
        for line in csvfile.readlines():
            arr = line.split(";")
            sgs98id = int(arr[0].removesuffix("."))
            id_if = int(arr[1])
            lat_name = arr[3]
            old_lat_name = arr[4]
            old_slo_name = arr[5]
            edibility = arr[6]
            if edibility.startswith("UN"):
                edibility = "užitnost neznana"
            elif edibility.startswith("PU"):
                edibility = "pogojno užitna"
            elif (edibility.startswith("SS")):
                edibility = "smrtno strupena"
            elif (edibility.startswith("S")):
                edibility = "strupena"
            elif (edibility.startswith("NU")):
                edibility = "neužitna"
            elif (edibility.startswith("MU")):
                edibility = "mlada užitna"
            elif (edibility.startswith("U")):
                edibility = "užitna"
            slo_name = ""
            if unidecode(old_lat_name) == unidecode(lat_name):
                slo_name = old_slo_name
            cursor.execute("SELECT id FROM vrste WHERE name = ?", (lat_name,))
            data = cursor.fetchall()
            if len(data) == 0:
                s = "INSERT INTO vrste(id_osgs, id_if, name, name_old, name_slo, name_slo_old, edibility) VALUES('{}','{}','{}','{}','{}','{}','{}')".format(sgs98id, id_if, lat_name, old_lat_name, slo_name, old_slo_name, edibility)
                cursor.execute(s)

conn = sqlite3.connect('gobe.db')

conn.execute('''CREATE TABLE IF NOT EXISTS vrste(
         id             INTEGER PRIMARY KEY AUTOINCREMENT,
         id_osgs        INTEGER DEFAULT 0 NOT NULL,
         id_if          INTEGER DEFAULT 0 NOT NULL,
         name           TEXT NOT NULL,
         name_slo       TEXT DEFAULT '',
         name_old       TEXT DEFAULT '',
         name_slo_old   TEXT DEFAULT '',
         link           TEXT,
         list80         INTEGER DEFAULT 0 NOT NULL,
         list240        INTEGER DEFAULT 0 NOT NULL,
         protected      INTEGER DEFAULT 0 NOT NULL,
         status         TEXT DEFAULT '',
         edibility      TEXT DEFAULT '',
         comment        TEXT DEFAULT '');''')
         
conn.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_name ON vrste(name);''')

conn.execute('''CREATE TABLE IF NOT EXISTS slike(
         id             INTEGER PRIMARY KEY AUTOINCREMENT,
         vrsta_id       INTEGER NOT NULL,
         link           TEXT NOT NULL,
         author         TEXT NOT NULL);''')

cursor = conn.cursor()

imenaOSGS2013 = []

extractOSGS2013()
extractFromCelotniSeznamURL("https://www.gobe.si/Gobe/Gobe")
extractFromCelotniSeznamURL("https://www.gobe.si/Protozoa")
checkUzitnost()
extractFromRdeciSeznamURL("https://www.gobe.si/Gobe/RdeciSeznam")
extractFromSeznamURL("https://www.gobe.si/Izobrazevanje/SeznamZacetni", "list80")
extractFromSeznamURL("https://www.gobe.si/Izobrazevanje/SeznamNadaljevalni", "list240")
extractFromZasciteniSeznamURL("https://www.gobe.si/Gobe/ZasciteneGobe")
#checkSlike()

#sqlite_select_query = '''SELECT * FROM vrste WHERE status != "" ORDER BY name ASC'''
#sqlite_select_query = '''SELECT * FROM vrste ORDER BY name ASC'''
sqlite_select_query = '''SELECT name_old, name_slo_old, name, name_slo FROM vrste WHERE name_old != "" AND id_osgs>0 AND name_slo == "" ORDER BY name ASC'''
cursor.execute(sqlite_select_query)
records = cursor.fetchall()
print("Total rows are:  ", len(records))
for row in records:
    print(row[0] + ", " + row[1] + " ===> " + row[2] + ", " + row[3])

#sqlite_select_query = '''SELECT * FROM slike'''
#cursor.execute(sqlite_select_query)
#records = cursor.fetchall()
#print("Total rows are:  ", len(records))
#for row in records:
#    print(row)

cursor.close()
conn.commit()
conn.close()
