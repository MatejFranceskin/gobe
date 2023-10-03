from fpdf import FPDF
from PIL import Image
import qrcode
import os
import requests
import sqlite3

class GobaOpis:
  def __init__(self, id, ime, latinsko_ime, uzitnost, status, url, slika):
    self.id = id
    self.ime = ime
    self.latinsko_ime = latinsko_ime
    self.uzitnost = uzitnost
    self.status = status
    self.url = url
    self.slika = slika

def createCard(pdf, x1, y1, x2, y2, opis):
    text1 = opis.ime.upper()
    text2 = opis.latinsko_ime
    text3 = opis.uzitnost.upper()
    text4 = opis.status.upper()
    text5 = str(opis.id)
    imagePath = opis.slika
    url = opis.url

    width = x2 - x1
    height = y2 - y1

    pdf.rect(x1, y1, width, height)

    image_width = 0.27 * width
    qr_image_width = 0.21 * width
    text1_margin_factor = 0.3
    text1_size_factor = 0.4
    text2_margin_factor = 0.2
    text2_size_factor = 0.3
    text5_size_factor = 0.15
    text1a_y = 0

    text1a = ""
    if (len(text1) > 14):
        t = text1.split()
        text1 = t[0]
        text1a = t[1]
        text1_margin_factor = 0.2
        text2_margin_factor = 0.18
    
    text_x = x1
    text1_y = y1 + text1_margin_factor * height
    text1_h = text1_size_factor * height
    last_y = text1_y

    if text1a:
        text1a_y = last_y + text2_margin_factor * height
        last_y = text1a_y

    text2_y = last_y + text2_margin_factor * height
    text2_h = text2_size_factor * height

    text3_y = text2_y + text2_margin_factor * height
    text3_h = text2_size_factor * height

    text4_y = text3_y + text2_margin_factor * height
    text4_h = text2_size_factor * height

    text5_h = text5_size_factor * height
    text5_y = y2


    if not text4:
        text1_y += 0.05 * height
        text1a_y += 0.05 * height
        text2_y += 0.05 * height
        text3_y += 0.05 * height

    pdf.set_font("ArialUni", '', text1_h)
    text1_width = pdf.get_string_width(text1)
    w = (width - text1_width - image_width) / 2
    pdf.text(text_x + w, text1_y, text1)

    if text1a:
        text1a_width = pdf.get_string_width(text1a)
        w = (width - text1a_width - image_width) / 2
        pdf.text(text_x + w, text1a_y, text1a)

    pdf.set_font("ArialUni", '', text2_h)
    text2_width = pdf.get_string_width(text2)
    w = (width - text2_width - image_width) / 2
    pdf.text(text_x + w, text2_y, text2)

    pdf.set_font("ArialUni", '', text3_h)
    text3_width = pdf.get_string_width(text3) + 0.2
    w = (width - text3_width - image_width) / 2
    if text3 == "UŽITNA" or text3 == "MLADA UŽITNA":
        pdf.set_fill_color(23, 189, 56)
    elif text3 == "POGOJNO UŽITNA":
        pdf.set_fill_color(227, 217, 18)
    elif text3 == "NEUŽITNA" or text3 == "UŽITNOST NEZNANA":
        pdf.set_fill_color(173, 117, 3)
    elif text3 == "STRUPENA":
        pdf.set_fill_color(255, 130, 3)
    elif text3 == "SMRTNO STRUPENA":
        pdf.set_fill_color(235, 64, 52)
    else:
        pdf.set_fill_color(255, 255, 255)

    pdf.rect(text_x + w - 1, text3_y - text3_h * 0.35 + 0.4, text3_width + 2, text3_h * 0.35 + 0.12, 'F')
    pdf.text(text_x + w, text3_y, text3)

    pdf.set_font("ArialUni", '', text4_h)
    text4_width = pdf.get_string_width(text4)
    w = (width - text4_width - image_width) / 2
    pdf.text(text_x + w, text4_y, text4)

#    im = Image.open(imagePath)
#    ratio = im.width / im.height
#    im.close()

#    image_y = y2 - image_width / ratio
    
    pdf.image(imagePath, x2 - image_width - 0.05 * height, y1 + 0.05 * height, image_width)

    img = qrcode.make(url)
    qrn = "qr"+ text2.strip() +".png"
    img.save(qrn)
    pdf.image(qrn, x2 - qr_image_width - 5, y2 - qr_image_width - 1, qr_image_width, qr_image_width)
    os.remove(qrn)

    pdf.set_font("ArialUni", '', text5_h)
    pdf.text(x2 - pdf.get_string_width(text5) - 2, text5_y - 1, text5)

def url_request_file(url, filename):
    while True:
        try:
            print("Getting " + url)
            response = requests.get(url, headers={"User-Agent": "Chrome/112.0.0.0"})
            with open(filename, "wb") as f:
                f.write(response.content)
            break
        except:
            print("Retrying " + url)

page_width = 210
page_height = 296
n_columns = 2
n_rows = 6
n_pages_per_pdf = 200
card_width = page_width / n_columns
card_height = page_height / n_rows

conn = sqlite3.connect('gobe.db')
cursor = conn.cursor()

opisi = []
sqlite_select_query = '''SELECT id,name,name_slo,link,protected,status,edibility FROM vrste ORDER BY name ASC'''
cursor.execute(sqlite_select_query)
records = cursor.fetchall()
for record in records:
#    if len(opisi) > 120:
#        break
    cursor.execute('''SELECT link FROM slike WHERE vrsta_id = ? LIMIT 1''', (record[0],))
    slike = cursor.fetchall()
    for slika in slike:
        url = slika[0]
        if url.endswith("Amanita_caesarea.jpg"):
            url = url[:-4] + "1.jpg"
        filename = "pictures/" + slika[0].split('/')[-1]
        if not os.path.isfile(filename):
            url_request_file(url, filename)
        status = ""
        if record[4]:
            status = "zavarovana vrsta"
        elif record[5] == "E":
            status = "prizadeta vrsta"
        elif record[5] == "V":
            status += "ranljiva vrsta"
        elif record[5] == "R":
            status += "redka vrsta"
        elif record[5] == "K" or record[6] == "I":
            status += "ogrožena vrsta"
        if status and record[5]:
            status += " (" + record[5] + ")"
        opisi.append(GobaOpis(record[0], record[2], record[1], record[6], status, record[3], filename))
        break

pdf_n = 1
opis_index = 0
num = len(opisi)

while opis_index < num:
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.add_font("ArialUni", "", "arialuni.ttf", uni=True)

    strani_n = 1
    while opis_index < num:
        for i in range(n_columns):
            for j in range(n_rows):
                createCard(pdf, i * card_width, j * card_height, (i + 1) * card_width, (j + 1) * card_height, opisi[opis_index])
                opis_index += 1
                if opis_index >= num:
                    break
            if opis_index >= num:
                break
        if opis_index < num:
            pdf.add_page()
            strani_n += 1

        if strani_n > n_pages_per_pdf:
            break;

    pdfname = "GobjeVizitke" + str(pdf_n) + ".pdf"
    pdf.output(pdfname, 'F')
    print("PDF " + str(pdf_n))
    pdf_n = pdf_n + 1

cursor.close()
conn.close()
