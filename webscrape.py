import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import sys
from unidecode import unidecode

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

def extractImageFromWikidata(vrsta_id, name):
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
                processSlikaURL(vrsta_id, "https://commons.wikimedia.org/wiki/File:" + image, "wikimedia")
                if (take_only_first_image):
                    return;

        for image in list:
            for s in srch:
                if s in image:
                    processSlikaURL(vrsta_id, "https://commons.wikimedia.org/wiki/File:" + image, "wikimedia")
                    if (take_only_first_image):
                        return;

        for image in list:
            processSlikaURL(vrsta_id, "https://commons.wikimedia.org/wiki/File:" + image, "wikimedia")
            if (take_only_first_image):
                return;

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
                if (take_only_first_image):
                    return;

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
                if (take_only_first_image):
                    return;
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
            
            if len(arr) < 4:
                continue
                
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
                name = unidecode(link.contents[0].strip())
                if name == "Laricifomes officinalis":
                    name = "Fomitopsis officinalis"
                if name == "Elaphocordyceps ophioglossoides":
                    name = "Tolypocladium ophioglossoides"
                if name == "Boletus fragrans":
                    name = "Lanmaoa fragrans"
                if name == "Leucopaxillus macrorhizus":
                    name = "Pogonoloma macrorhizum"
                if name == "Bondarzewia montana":
                    name = "Bondarzewia mesenterica"
                sys.stdout.buffer.write(name.encode('utf8'))
                sys.stdout.buffer.write('\n'.encode('utf8'))
                s = "UPDATE vrste SET protected = 1 WHERE name = '{}'".format(name)
                cursor.execute(s)
                s = "UPDATE vrste SET protected = 1 WHERE name_old = '{}'".format(name)
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
                elif (edibility.startswith("užiten")):
                    edibility = "užitna"
                elif (edibility.startswith("užitna")):
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

            if "SINONIMI" in srow:
                if name in ["Amanita battarrae", "Russula camarophylla", "Neoboletus luridiformis", "Limacella delicata", "Hygrophorus persicolor", "Craterellus undulatus", "Bovistella utriformis", "Ceriporia reticulata", "Psathyrella vernalis", "Lepiota helveola", "Lepiota brunneolilacea"]:
                    continue
                srow = srow.removeprefix('<p class="vspace">').replace('<strong>', '').replace('</strong>', '').replace('</p>', '').replace('<span class="-pm--3">', '').replace('</span>', '').strip()
                sinonimi = srow.removeprefix('SINONIMI: ')
                sin_arr = []
                for sin in sinonimi.split(','):
                    s_i = sin.find("<em>")
                    e_i = sin.find("</em>")
                    if (s_i != -1 and e_i != -1):
                        sin_arr.append(sin[s_i+4:e_i])

                found = False
                for staroIme in imenaOSGS2013:
                    if name == staroIme[0]:
                        found = True
                        break

                if not found:
                    for staroIme in imenaOSGS2013:
                        if staroIme[0] in sin_arr:
#                            print(oldName + " ---> " + name)
                            s = "UPDATE vrste SET name_old = '{}', name_slo_old = '{}' WHERE id = {}".format(staroIme[0], staroIme[1], id)
                            cursor.execute(s)
                            break

            if "SGS2020: " in srow:
                s_i = srow.find("SGS2020: ")
                e_i = srow.find("</span>")
                sgs2020 = srow[s_i+9:e_i]
                s = "UPDATE vrste SET sgs2020 = {} WHERE id = {}".format(sgs2020, id)
                cursor.execute(s)
            if "<p><strong>" in srow:
                s_i = srow.find("<p><strong>")
                e_i = srow.find("</strong>")
                full_name = srow[s_i+11:e_i]
#                print("full_name: " + full_name)
                s = "UPDATE vrste SET full_name = '{}' WHERE id = {}".format(full_name, id)
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
#            extractImageFromWikidata(record[0], record[1])
    conn.commit()

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

#        print(words[0].replace('.', '') + " # " + name + " # " + slo_name)
        imenaOSGS2013.append((unidecode(name.strip()), slo_name.strip()))

def extractFromGobeVPripraviPages():
    """
    Read gobe_v_pripravi_pages.txt and add entries to database if latin name doesn't exist
    File format: URL;LatinName;SlovenianName;FullName;Uzitnost
    """
    try:
        with open('gobe_v_pripravi_pages.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        # Skip header line
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            # Split by semicolon
            parts = line.split(';')
            if len(parts) < 5:
                continue
                
            url = parts[0].strip()
            latin_name = parts[1].strip()
            slovenian_name = parts[2].strip()
            full_name = parts[3].strip()
            uzitnost = parts[4].strip()
            
            # Skip if latin name is empty
            if not latin_name:
                continue
                
            # Check if this latin name already exists in database
            cursor.execute("SELECT id FROM vrste WHERE name = ?", (latin_name,))
            existing = cursor.fetchall()
            
            if len(existing) == 0:
                # Insert new entry
                print(f"Adding new entry: {latin_name} - {slovenian_name}")
                cursor.execute('''INSERT INTO vrste(name, name_slo, full_name, link, edibility) 
                                 VALUES(?, ?, ?, ?, ?)''', 
                              (latin_name, slovenian_name, full_name, url, uzitnost))
            else:
                # Update existing entry with additional information
                print(f"Updating existing entry: {latin_name}")
                cursor.execute('''UPDATE vrste SET 
                                 name_slo = CASE WHEN name_slo = '' THEN ? ELSE name_slo END,
                                 full_name = CASE WHEN full_name = '' THEN ? ELSE full_name END,
                                 link = CASE WHEN link IS NULL OR link = '' THEN ? ELSE link END,
                                 edibility = CASE WHEN edibility = '' THEN ? ELSE edibility END
                                 WHERE name = ?''', 
                              (slovenian_name, full_name, url, uzitnost, latin_name))
        
        conn.commit()
        print("Successfully processed gobe_v_pripravi_pages.txt")
        
    except FileNotFoundError:
        print("Error: gobe_v_pripravi_pages.txt not found")
    except Exception as e:
        print(f"Error processing file: {e}")

def extractFromImena():
    """
    Read imena.csv and add entries to database if latin name doesn't exist
    CSV format: ID;Status;LatinNameWithDiacritics;Author;SlovenianName
    We skip records where Status (field 2) is "sin"
    """
    try:
        with open('imena.csv', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Split by semicolon
            parts = line.split(';')
            if len(parts) < 5:
                continue
                
            id_field = parts[0].strip()
            status_field = parts[1].strip()
            latin_name_with_diacritics = parts[2].strip()
            author_field = parts[3].strip()
            slovenian_name = parts[4].strip()
            
            # Skip records where status field is "sin"
            if status_field == "sin":
                continue
                
            # Skip if latin name is empty
            if not latin_name_with_diacritics:
                continue
                
            # Remove diacritical signs from latin name
            latin_name = unidecode(latin_name_with_diacritics)
            
            # Compose full name from latin name with diacritics + author
            full_name = latin_name_with_diacritics + " " + author_field
            
            # Check if this latin name already exists in database
            cursor.execute("SELECT id FROM vrste WHERE name = ?", (latin_name,))
            existing = cursor.fetchall()
            
            if len(existing) == 0:
                # Insert new entry with empty URL and "užitnost neznana"
                print(f"Adding new entry from imena.csv: {latin_name} - {slovenian_name}")
                cursor.execute('''INSERT INTO vrste(name, name_slo, full_name, link, edibility) 
                                 VALUES(?, ?, ?, '', 'užitnost neznana')''', 
                              (latin_name, slovenian_name, full_name))
            else:
                # Entry already exists in DB, do not update
                print(f"Entry already exists, skipping: {latin_name}")
        
        conn.commit()
        print("Successfully processed imena.csv")
        
    except FileNotFoundError:
        print("Error: imena.csv not found")
    except Exception as e:
        print(f"Error processing imena.csv: {e}")

def checkURLs():
    """
    Check for Wikipedia pages for all entries in the database.
    Priority: 1) Always prefer Slovenian Wikipedia if available
             2) Use English Wikipedia if no Slovenian exists and (no current URL or current URL is broken)
    """
    print("Checking Wikipedia URLs for all entries...")
    
    try:
        # Get all entries from the database
        cursor.execute("SELECT id, name, name_slo, link FROM vrste")
        records = cursor.fetchall()
        
        updated_count = 0
        total_count = len(records)
        
        for i, (entry_id, latin_name, slovenian_name, current_url) in enumerate(records):
            print(f"Processing {i+1}/{total_count}: {latin_name}")
            
            new_url = None
            update_reason = ""
            
            # Always check for Slovenian Wikipedia first - it has highest priority
            sl_wiki_url = f"https://sl.wikipedia.org/wiki/{latin_name.replace(' ', '_')}"
            try:
                response = url_request(sl_wiki_url)
                if response.status_code == 200:
                    # Check if it's not a redirect to a disambiguation or non-existent page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Check if page exists (not a "page does not exist" message)
                    if not soup.find('div', {'class': 'noarticletext'}):
                        # Check if current URL is already this Slovenian Wikipedia page
                        if current_url != sl_wiki_url:
                            new_url = sl_wiki_url
                            update_reason = "Found Slovenian Wikipedia (priority over existing URL)"
                            print(f"  Found Slovenian Wikipedia: {sl_wiki_url}")
                        else:
                            print(f"  Already has Slovenian Wikipedia URL: {sl_wiki_url}")
            except:
                pass
            
            # If no Slovenian Wikipedia found, check English Wikipedia
            # But only update if current URL is empty, broken, or doesn't exist
            if not new_url:
                current_url_valid = False
                
                # Check if current URL is valid and working
                if current_url and current_url.strip() != "":
                    try:
                        response = url_request(current_url)
                        if response.status_code == 200:
                            current_url_valid = True
                    except:
                        pass
                
                # Only try English Wikipedia if current URL is invalid or empty
                if not current_url_valid:
                    en_wiki_url = f"https://en.wikipedia.org/wiki/{latin_name.replace(' ', '_')}"
                    try:
                        response = url_request(en_wiki_url)
                        if response.status_code == 200:
                            # Check if it's not a redirect to a disambiguation or non-existent page
                            soup = BeautifulSoup(response.text, 'html.parser')
                            # Check if page exists (not a "page does not exist" message)
                            if not soup.find('div', {'class': 'noarticletext'}):
                                new_url = en_wiki_url
                                if not current_url or current_url.strip() == "":
                                    update_reason = "Found English Wikipedia (no existing URL)"
                                else:
                                    update_reason = "Found English Wikipedia (replacing broken URL)"
                                print(f"  Found English Wikipedia: {en_wiki_url}")
                    except:
                        pass
                else:
                    print(f"  Current URL is valid, keeping: {current_url}")
            
            # Update database if we found a better Wikipedia page
            if new_url:
                cursor.execute("UPDATE vrste SET link = ? WHERE id = ?", (new_url, entry_id))
                updated_count += 1
                print(f"  Updated URL for {latin_name} - {update_reason}")
            elif not current_url or current_url.strip() == "":
                print(f"  No Wikipedia page found for {latin_name}")
            else:
                print(f"  Keeping existing URL for {latin_name}")
        
        conn.commit()
        print(f"Successfully processed {total_count} entries, updated {updated_count} URLs")
        
    except Exception as e:
        print(f"Error in checkURLs: {e}")

conn = sqlite3.connect('gobe.db')

conn.execute('''CREATE TABLE IF NOT EXISTS vrste(
         id             INTEGER PRIMARY KEY AUTOINCREMENT,
         name           TEXT NOT NULL,
         name_slo       TEXT NOT NULL,
         name_old       TEXT DEFAULT '',
         name_slo_old   TEXT DEFAULT '',
         full_name      TEXT DEFAULT '',
         link           TEXT,
         list80         INTEGER DEFAULT 0 NOT NULL,
         list240        INTEGER DEFAULT 0 NOT NULL,
         protected      INTEGER DEFAULT 0 NOT NULL,
         sgs2020        INTEGER DEFAULT 0 NOT NULL,
         status         TEXT DEFAULT '',
         edibility      TEXT DEFAULT '',
         comment        TEXT DEFAULT '');''')
         
conn.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_name ON vrste(name);''')

#conn.execute('''DROP TABLE IF EXISTS slike''')

conn.execute('''CREATE TABLE IF NOT EXISTS slike(
         id             INTEGER PRIMARY KEY AUTOINCREMENT,
         vrsta_id       INTEGER NOT NULL,
         link           TEXT NOT NULL,
         author         TEXT NOT NULL);''')

cursor = conn.cursor()

take_only_first_image = True
imenaOSGS2013 = []

extractOSGS2013()
extractFromCelotniSeznamURL("https://www.gobe.si/Gobe/Gobe")
extractFromCelotniSeznamURL("https://www.gobe.si/Protozoa")
extractFromCelotniSeznamURL("https://www.gobe.si/Lisaji/Lisaji")
checkUzitnost()
extractFromRdeciSeznamURL("https://www.gobe.si/Gobe/RdeciSeznam")
extractFromSeznamURL("https://www.gobe.si/Izobrazevanje/SeznamZacetni", "list80")
extractFromSeznamURL("https://www.gobe.si/Izobrazevanje/SeznamNadaljevalni", "list240")
extractFromZasciteniSeznamURL("https://www.gobe.si/Gobe/ZasciteneGobe")
extractFromGobeVPripraviPages()
extractFromImena()
checkURLs()
#checkSlike()

#sqlite_select_query = '''SELECT * FROM vrste WHERE status != "" ORDER BY name ASC'''
#sqlite_select_query = '''SELECT name, name_slo, link FROM vrste ORDER BY name ASC'''
#cursor.execute(sqlite_select_query)
#records = cursor.fetchall()
#print("Total rows are:  ", len(records))
#for row in records:
#    print(row[0] + ";" + row[1] + ";" + row[2])

#sqlite_select_query = '''SELECT * FROM slike'''
#cursor.execute(sqlite_select_query)
#records = cursor.fetchall()
#print("Total rows are:  ", len(records))
#for row in records:
#    print(row)

#print("#######################################################")
#print("Stara imena, ki manjkajo v bazi:")
#for staroIme in imenaOSGS2013:
#    oldName = staroIme[0]
#    cursor.execute('''SELECT id FROM vrste WHERE name = ? OR name_old = ?''', (oldName,oldName))
#    records = cursor.fetchall()
#    if not records:
#        print(oldName + "; " + staroIme[1])
#        continue
#print("#######################################################")

#sqlite_select_query = '''SELECT * FROM vrste WHERE protected != 0 ORDER BY name ASC'''
#cursor.execute(sqlite_select_query)
#records = cursor.fetchall()
#for row in records:
#    sys.stdout.buffer.write(row[1].encode('utf8'))
#    sys.stdout.buffer.write('\n'.encode('utf8'))
#print("Total rows are:  ", len(records))

cursor.close()
conn.commit()
conn.close()
