import requests
import sqlite3
import sys

def url_request(url):
    while True:
        try:
#            print("Getting " + url)
            response = requests.get(url, headers={"User-Agent": "Chrome/112.0.0.0"})
            return response
        except:
            print("Retrying " + url)

conn = sqlite3.connect('gobe.db')
cursor = conn.cursor()

utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)

rod = sys.argv[1]
name = sys.argv[1] + " " + sys.argv[2]
name_wiki = sys.argv[1] + "_" + sys.argv[2]
name_gobe = sys.argv[1] + sys.argv[2].title()
if len(sys.argv) > 4:
    name_slo = sys.argv[3] + " " + sys.argv[4]
else:
    cursor.execute("SELECT name_slo FROM vrste WHERE name='{}'".format(name))
    records = cursor.fetchall()
    for row in records:
        name_slo = row[0]
        break
        
a = name_slo.split(" ")
rod_slo = a[1]
name_slo_cap = a[0].title()+" "+a[1]

url = str(r'https://en.wikipedia.org/w/rest.php/v1/page/') + name_wiki
response = url_request(url)

src = response.json()["source"]
i = src.find("{{Speciesbox")
speciesbox = ""
if i > -1:
    j = src.find("}}", i)
    if j > -1:
        k = src.find("{{", i+2, j)
        if k != -1:
            j = src.find("}}", j+2)
        if j > -1:
            speciesbox = src[i:j+2]

i = src.find("{{Taxonbar")
if i == -1:
    exit(1)
j = src.find("}}", i)
if j == -1:
    exit(1)
taxonbar = src[i:j+2]

new_speciesbox = ""
if speciesbox != "":
    new_sa = []
    for sa in speciesbox.split("|"):
        if "{{Speciesbox" in sa:
            new_sa.append(sa)
            new_sa.append(" name = " + name_slo_cap + "\n")
            new_sa.append(" taxon = " + name + "\n")
            continue
        if "taxon" in sa:
            continue
        if "name" in sa:
            continue
        if "genus" in sa:
            continue
        if "species" in sa:
            continue
        new_sa.append(sa)
    new_speciesbox = "|".join(new_sa)
else:
    new_speciesbox = "{{Speciesbox\n| name = " + name_slo_cap + "\n| taxon = " + name + "\n| image = \n| authority = \n| synonyms = \n}}"

print('{{Short description|Vrsta glive}}', file=utf8stdout)
print(new_speciesbox, file=utf8stdout)
print("", file=utf8stdout)
print("'''{}''' ([[Znanstvena klasifikacija živih bitij|znanstveno ime]] '''''{}''''') je [[gliva]] iz rodu [[{}|{} (''{}'')]].".format(name_slo_cap, name, rod_slo, rod_slo, rod), file=utf8stdout)
print("", file=utf8stdout)
print("== Značilnosti ==", file=utf8stdout)

print("Klobuk\n", file=utf8stdout)
print("Trosovnica\n", file=utf8stdout)
print("Bet\n", file=utf8stdout)
print("Meso\n", file=utf8stdout)
print("== Razširjenost in življenjski prostor ==", file=utf8stdout)
print("== Mikroskopske značilnosti ==", file=utf8stdout)
print("== Podobne vrste ==", file=utf8stdout)
print("== Uporabnost ==", file=utf8stdout)
print("== Taksonomija ==", file=utf8stdout)
print("== Galerija slik ==", file=utf8stdout)
print("{{Galerija", file=utf8stdout)
print("| Tulostoma brumale 343884743.jpg | Opis", file=utf8stdout)
print("}}", file=utf8stdout)
print("== Zunanje povezave ==", file=utf8stdout)
print("{{{{Commons|category:{}}}}}".format(name), file=utf8stdout)
print("* [https://www.gobe.si/Gobe/{} www.gobe.si]".format(name_gobe), file=utf8stdout)
print("== Sklici ==", file=utf8stdout)
print("{{sklici}}", file=utf8stdout)
print(taxonbar, file=utf8stdout)
print("{{normativna kontrola}}", file=utf8stdout)
print("[[Kategorija:Užitne_gobe]]", file=utf8stdout)
print("[[Kategorija:Neužitne gobe]]", file=utf8stdout)
print("[[Kategorija:Pogojno užitne gobe]]", file=utf8stdout)
print("[[Kategorija:Strupene_gobe]]", file=utf8stdout)
print("[[Kategorija:Prostotrosnice]]", file=utf8stdout)
print("[[Kategorija:Zaprtotrosnice]]", file=utf8stdout)
print("[[Kategorija:Vrste_gliv]]", file=utf8stdout)
print("[[Kategorija:Najmanj_ogrožene_vrste]]", file=utf8stdout)
print("[[Kategorija:Potencialno_ogrožene_vrste]]", file=utf8stdout)

cursor.close()
conn.close()


#{{Speciesbox
#| image = 2009-10-23 Leucoagaricus leucothites (Vittad.) M.M. Moser ex Bon 61894 crop.jpg
#| taxon = Leucoagaricus leucothites
#| authority = ([[Vittad.]]) Wasser (1977)
#| synonyms = *''Agaricus leucothites'' <small>Vittad. (1835)</small>
#*''Lepiota holosericea'' <small>(J.&nbsp;J. Planer) [[Claude Casimir Gillet|Gillet]] (1874)</small>
#*''Leucoagaricus naucinus''<ref>{{Cite web|last=Wood|first=Michael|last2=Stevens|first2=Fred|title=California Fungi: Leucoagaricus leucothites|url=http://www.mykoweb.com/CAF/species/Leucoagaricus_leucothites.html|access-date=2021-02-15|website=MykoWeb}}</ref> <small>Singer</small>
#*''Leucocoprinus holosericeus'' <small>(J.&nbsp;J. Planer) [[Locq.]] (1943)</small>
#}}
