from bs4 import BeautifulSoup
import sys
import sqlite3
import requests
from unidecode import unidecode
from datetime import datetime

def url_request(url):
    while True:
        try:
#            print("Getting " + url)
            response = requests.get(url, headers={"User-Agent": "Chrome/112.0.0.0"})
            return response
        except:
            print("Retrying " + url)

def extractImageFromWikidata(name):
    pic_searches = [name.replace(" ", "+").replace("-", "+").replace("_", "+").replace("var.", "+")]
    for pic_search in pic_searches:
        url = str(r'https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo|categories&+generator=search&gsrsearch=File:') + str(pic_search) + str('&format=jsonfm&origin=*&iiprop=extmetadata&iiextmetadatafilter=ImageDescription|ObjectName')
        response = url_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        spans = soup.find_all('span', {'class': 's2'})
        lines = [span.get_text() for span in spans]
        new_list = [item.replace('"', '') for item in lines]
        new_list2 = [x for x in new_list if x.startswith('File')]
        new_list3 = [x[5:] for x in new_list2]
        new_list4 = [x.replace(' ','_') for x in new_list3]
        list = []
        for image in new_list4:
            if image.lower().endswith(".pdf") or image.lower().endswith(".png") or image.lower().endswith(".svg"):
                continue;
            i = image.find("\\")
            if (i >= 0 and len(image) > i + 1 and image[i + 1] != "u"):
                continue
            if (image.count(".") > 1):
                continue
            list.append(image);

        srch = pic_search.split('+')
        for image in list:
            found = True
            for s in srch:
                if s not in image:
                    found = False
                    break
            if found:   
                return image

        for image in list:
            for s in srch:
                if s in image:
                    return image

        for image in list:
            return image

def extractImena():
    file = open('imena.csv', mode="r", encoding="utf-8")
    for line in file.readlines():
        if line.startswith(";sin;"):
            continue
        l = line.split(";")

        if (len(l) < 5):
            continue
        
        name = l[2].strip()
        slo_name = l[4].strip()
        imena.append((unidecode(name), slo_name))

rod = sys.argv[1]
rod_slo = sys.argv[2]
imena = []
extractImena()

conn = sqlite3.connect('gobe.db')
cursor = conn.cursor()
cursor.execute("SELECT name, name_slo FROM vrste WHERE name like '%{}%' ORDER BY name_slo".format(rod))
records = cursor.fetchall()
for row in records:
   if (not row in imena):
        imena.append((row[0], row[1]))

print('{{Short description|rod gliv}}')
print('{{Automatic taxobox')
print('| taxon = ' + rod)
print('| diversity = vrst')
print('| diversity_ref = <ref>{{{{Navedi splet|title={} {{{{!}}}} COL|url=https://www.catalogueoflife.org/data/taxon/54HL|website=www.catalogueoflife.org|accessdate={}}}}}</ref>'.format(rod, datetime.today().strftime('%Y-%m-%d')))
print('}}')
print('')
print("'''{}''' ([[Znanstvena klasifikacija živih bitij|znanstveno ime]] '''''{}''''') so [[rod (biologija)|rod]] [[glive|gliv]] iz [[družina (biologija)|družine]] [[cevarke|cevark]] (''Boletaceae'').".format(rod_slo, rod))
print('')
print('== Seznam {} Slovenije<ref>{{{{Navedi knjigo|title=Seznam gliv Slovenije|publisher=Mikološka zveza Slovenije|year=2022|isbn=978-961-90647-2-6|cobiss=130237443}}}}</ref> =='.format(rod_slo))

for row in imena:
    if not row[0].startswith(rod + " "):
        continue
    print("*[[{}]] (''{}'')".format(row[1], row[0]))
print('')
   
print('== Sklici ==')
print('{{sklici}}')
print('')
print('== Zunanje povezave ==')
print('{{{{Commons|category:{}}}}}'.format(rod))
print('* [http://www.gobe.si/Mikologija/{} {} na www.gobe.si]'.format(rod, rod_slo))
print('')
print('{{Taxonbar}}')
print('{{normativna kontrola}}')
print('')
print('[[Kategorija:rodovi gliv]]')
print('[[Kategorija:cevarke]]')
print('[[Kategorija:Taksoni, opisani leta 1822]]')

